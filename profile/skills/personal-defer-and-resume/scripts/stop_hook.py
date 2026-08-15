#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shlex
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if os.name == "posix":
    import fcntl
elif os.name == "nt":
    import msvcrt


def positive_seconds(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return value if value > 0 else default


POLL_SECONDS = positive_seconds("CODEX_DEFER_POLL_SECONDS", 0.5)
REARM_SECONDS = 3000.0
WAKE_RETRY_SECONDS = positive_seconds("CODEX_DEFER_WAKE_RETRY_SECONDS", 60.0)
MAX_WAKE_ATTEMPTS = 3
RESULT_STALE_WORKER = 125


def emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False))
    sys.stdout.flush()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME", "").strip()
    return Path(configured).expanduser().resolve() if configured else Path.home() / ".codex"


def runtime_root() -> Path:
    override = os.environ.get("CODEX_DEFER_RUNTIME", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return codex_home() / "runtime" / "personal-defer-and-resume"


def current_thread(hook_input: dict[str, Any]) -> str:
    for candidate in (
        os.environ.get("CODEX_THREAD_ID"),
        hook_input.get("thread_id"),
        hook_input.get("threadId"),
        hook_input.get("session_id"),
        hook_input.get("sessionId"),
    ):
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return ""


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if os.name == "posix":
        os.chmod(temporary, 0o600)
    temporary.replace(path)
    if os.name == "posix":
        os.chmod(path, 0o600)


def open_worker_lock(task_dir: Path) -> int:
    descriptor = os.open(task_dir / "worker.lock", os.O_RDWR | os.O_CREAT, 0o600)
    if os.name == "nt" and os.fstat(descriptor).st_size == 0:
        os.write(descriptor, b"\0")
        os.fsync(descriptor)
    return descriptor


def try_worker_lock(descriptor: int) -> bool:
    if os.name == "posix":
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return False
        return True
    if os.name == "nt":
        os.lseek(descriptor, 0, os.SEEK_SET)
        try:
            msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
        except OSError:
            return False
        return True
    raise RuntimeError(f"unsupported platform: {os.name}")


def release_worker_lock(descriptor: int) -> None:
    if os.name == "posix":
        fcntl.flock(descriptor, fcntl.LOCK_UN)
    elif os.name == "nt":
        os.lseek(descriptor, 0, os.SEEK_SET)
        msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)


def worker_holds_lock(task_dir: Path) -> bool:
    worker_path = task_dir / "worker.json"
    if not worker_path.exists():
        return False
    descriptor = open_worker_lock(task_dir)
    try:
        if not try_worker_lock(descriptor):
            return True
        release_worker_lock(descriptor)
        return False
    finally:
        os.close(descriptor)


def synthesize_stale_result(task_dir: Path) -> None:
    result_path = task_dir / "result.json"
    worker_path = task_dir / "worker.json"
    if result_path.exists() or not worker_path.exists() or worker_holds_lock(task_dir):
        return
    metadata = read_json(task_dir / "metadata.json")
    worker = read_json(worker_path)
    write_json_atomic(
        result_path,
        {
            "task_id": metadata["task_id"],
            "name": metadata["name"],
            "started_at": worker.get("started_at"),
            "completed_at": now_iso(),
            "exit_code": RESULT_STALE_WORKER,
            "error": "worker exited without writing result.json",
            "timed_out": False,
            "log_path": str(task_dir / "output.log"),
        },
    )


def active_tasks(thread_dir: Path) -> list[Path]:
    if not thread_dir.is_dir():
        return []
    tasks: list[Path] = []
    for child in sorted(thread_dir.iterdir()):
        if not child.is_dir() or not (child / "metadata.json").is_file() or (child / "ack.json").exists():
            continue
        synthesize_stale_result(child)
        tasks.append(child)
    return tasks


def wake_attempt(task_dir: Path) -> int:
    wake_path = task_dir / "wake.json"
    if not wake_path.exists():
        return 0
    try:
        value = int(read_json(wake_path).get("attempt", 1))
    except (TypeError, ValueError):
        return 1
    return max(1, value)


def wake_due_in(task_dir: Path) -> float | None:
    if not (task_dir / "result.json").exists():
        return None
    if wake_attempt(task_dir) >= MAX_WAKE_ATTEMPTS:
        return None
    wake_path = task_dir / "wake.json"
    if not wake_path.exists():
        return 0.0
    try:
        elapsed = (datetime.now(timezone.utc) - parse_iso(str(read_json(wake_path)["emitted_at"]))).total_seconds()
    except Exception:
        return 0.0
    return max(0.0, WAKE_RETRY_SECONDS - elapsed)


def emit_completion(tasks: list[Path]) -> None:
    summaries: list[str] = []
    for task_dir in tasks:
        metadata = read_json(task_dir / "metadata.json")
        result = read_json(task_dir / "result.json")
        attempt = wake_attempt(task_dir) + 1
        write_json_atomic(
            task_dir / "wake.json",
            {
                "emitted_at": now_iso(),
                "exit_code": result.get("exit_code"),
                "attempt": attempt,
                "max_attempts": MAX_WAKE_ATTEMPTS,
            },
        )
        resume_command = shlex.join(
            [
                sys.executable,
                str(Path(__file__).with_name("defer.py")),
                "resume",
                "--task-dir",
                str(task_dir),
            ]
        )
        summaries.append(
            f"{metadata.get('name', task_dir.name)} exited with code {result.get('exit_code')}; "
            f"task directory: {task_dir}; resume command: {resume_command}"
        )
    emit(
        {
            "decision": "block",
            "reason": "Deferred command or watchdog exited. Inspect bounded result evidence, acknowledge the wake, then continue the original task. Treat watcher exit as attention rather than authority to control the underlying job.\n"
            + "\n".join(summaries),
        }
    )


def main() -> int:
    try:
        hook_input = json.load(sys.stdin)
        if not isinstance(hook_input, dict):
            hook_input = {}
    except Exception:
        hook_input = {}
    thread = current_thread(hook_input)
    if not thread:
        emit({"continue": True, "systemMessage": "personal-defer-and-resume: missing Codex thread id"})
        return 0

    thread_dir = runtime_root() / thread
    deadline = time.monotonic() + REARM_SECONDS
    try:
        while True:
            tasks = active_tasks(thread_dir)
            if not tasks:
                emit({"continue": True})
                return 0
            due = [task for task in tasks if wake_due_in(task) == 0.0]
            if due:
                emit_completion(due)
                return 0
            incomplete = [task for task in tasks if not (task / "result.json").exists()]
            retryable = [
                task
                for task in tasks
                if (task / "result.json").exists()
                and wake_attempt(task) < MAX_WAKE_ATTEMPTS
            ]
            if not incomplete and not retryable:
                emit({"continue": True})
                return 0
            remaining = deadline - time.monotonic()
            if incomplete and remaining <= 0:
                names = [str(read_json(task / "metadata.json").get("name", task.name)) for task in incomplete]
                emit(
                    {
                        "decision": "block",
                        "reason": "Deferred wait re-arm: still running: "
                        + ", ".join(names)
                        + ". Do not poll, inspect, or call tools. End this turn immediately so the local Stop hook can resume waiting.",
                    }
                )
                return 0
            retry_delays = [
                delay
                for task in retryable
                if (delay := wake_due_in(task)) is not None and delay > 0
            ]
            sleep_for = min(POLL_SECONDS, max(0.01, remaining)) if incomplete else POLL_SECONDS
            if retry_delays:
                sleep_for = min(sleep_for, max(0.01, min(retry_delays)))
            time.sleep(sleep_for)
    except Exception as exc:
        emit(
            {
                "decision": "block",
                "reason": f"Deferred wait state needs attention: {type(exc).__name__}: {exc}",
            }
        )
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
