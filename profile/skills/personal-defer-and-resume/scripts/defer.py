#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if os.name == "posix":
    import fcntl


RESULT_TIMEOUT = 124
RESULT_STALE_WORKER = 125


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME", "").strip()
    return Path(configured).expanduser().resolve() if configured else Path.home() / ".codex"


def runtime_root() -> Path:
    override = os.environ.get("CODEX_DEFER_RUNTIME", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return codex_home() / "runtime" / "personal-defer-and-resume"


def thread_id() -> str:
    value = os.environ.get("CODEX_THREAD_ID", "").strip()
    if not value:
        raise SystemExit("CODEX_THREAD_ID is unavailable; run this from a Codex task")
    return value


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if os.name == "posix":
        os.chmod(path.parent, 0o700)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if os.name == "posix":
        os.chmod(temporary, 0o600)
    temporary.replace(path)
    if os.name == "posix":
        os.chmod(path, 0o600)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def validate_task_dir(value: str) -> Path:
    task_dir = Path(value).expanduser().resolve()
    root = runtime_root().resolve()
    if root not in task_dir.parents or not (task_dir / "metadata.json").is_file():
        raise SystemExit(f"not a personal-defer-and-resume task directory: {task_dir}")
    return task_dir


def create_private_file(path: Path) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    os.close(descriptor)
    if os.name == "posix":
        os.chmod(path, 0o600)


def write_result_if_absent(task_dir: Path, value: dict[str, Any]) -> bool:
    path = task_dir / "result.json"
    if path.exists():
        return False
    write_json_atomic(path, value)
    return True


def worker_holds_lock(task_dir: Path) -> bool:
    worker_path = task_dir / "worker.json"
    if not worker_path.exists():
        return False
    if os.name != "posix":
        pid = int(read_json(worker_path).get("pid", 0))
        try:
            os.kill(pid, 0)
            return pid > 0
        except (OSError, ValueError):
            return False
    lock_path = task_dir / "worker.lock"
    descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        return False
    finally:
        os.close(descriptor)


def stale_worker_result(task_dir: Path) -> dict[str, Any] | None:
    result_path = task_dir / "result.json"
    if result_path.exists():
        return read_json(result_path)
    worker_path = task_dir / "worker.json"
    if not worker_path.exists() or worker_holds_lock(task_dir):
        return None
    metadata = read_json(task_dir / "metadata.json")
    worker_info = read_json(worker_path)
    write_result_if_absent(
        task_dir,
        {
            "task_id": metadata["task_id"],
            "name": metadata["name"],
            "started_at": worker_info.get("started_at"),
            "completed_at": now_iso(),
            "exit_code": RESULT_STALE_WORKER,
            "error": "worker exited without writing result.json",
            "timed_out": False,
            "log_path": str(task_dir / "output.log"),
        },
    )
    return read_json(result_path)


def terminate_process_group(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=2)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait()


def worker(task_dir: Path) -> int:
    if os.name != "posix":
        raise SystemExit("personal-defer-and-resume supports macOS and Linux")
    metadata = read_json(task_dir / "metadata.json")
    command = json.load(sys.stdin)
    if not isinstance(command, list) or not command or not all(isinstance(item, str) for item in command):
        raise SystemExit("worker command payload must be a non-empty JSON string array")

    lock_path = task_dir / "worker.lock"
    lock_descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
    fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
    started_at = now_iso()
    write_json_atomic(task_dir / "worker.json", {"pid": os.getpid(), "started_at": started_at})
    log_path = task_dir / "output.log"
    create_private_file(log_path)
    exit_code = 127
    error: str | None = None
    timed_out = False
    process: subprocess.Popen[bytes] | None = None
    try:
        with log_path.open("ab", buffering=0) as log_file:
            process = subprocess.Popen(
                command,
                cwd=metadata["cwd"],
                stdin=subprocess.DEVNULL,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                close_fds=True,
            )
            try:
                exit_code = process.wait(timeout=metadata.get("timeout_seconds"))
            except subprocess.TimeoutExpired:
                timed_out = True
                exit_code = RESULT_TIMEOUT
                error = f"command exceeded timeout of {metadata.get('timeout_seconds')} seconds"
                terminate_process_group(process)
                log_file.write((error + "\n").encode())
    except Exception as exc:
        if process is not None:
            terminate_process_group(process)
        error = f"{type(exc).__name__}: {exc}"
        with log_path.open("ab", buffering=0) as log_file:
            log_file.write((error + "\n").encode())
    finally:
        write_result_if_absent(
            task_dir,
            {
                "task_id": metadata["task_id"],
                "name": metadata["name"],
                "started_at": started_at,
                "completed_at": now_iso(),
                "exit_code": exit_code,
                "error": error,
                "timed_out": timed_out,
                "log_path": str(log_path),
            },
        )
        fcntl.flock(lock_descriptor, fcntl.LOCK_UN)
        os.close(lock_descriptor)
    return 0


def start(args: argparse.Namespace) -> int:
    if os.name != "posix":
        raise SystemExit("personal-defer-and-resume supports macOS and Linux")
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        raise SystemExit("a command is required after --")
    if args.timeout is not None and args.timeout <= 0:
        raise SystemExit("--timeout must be greater than zero")
    cwd = Path(args.cwd).expanduser().resolve()
    if not cwd.is_dir():
        raise SystemExit(f"working directory does not exist: {cwd}")

    task_id = uuid.uuid4().hex
    task_dir = runtime_root() / thread_id() / task_id
    task_dir.mkdir(parents=True, mode=0o700)
    os.chmod(task_dir, 0o700)
    write_json_atomic(
        task_dir / "metadata.json",
        {
            "version": 1,
            "task_id": task_id,
            "thread_id": thread_id(),
            "name": args.name,
            "cwd": str(cwd),
            "executable": Path(command[0]).name,
            "argument_count": max(0, len(command) - 1),
            "timeout_seconds": args.timeout,
            "registered_at": now_iso(),
        },
    )
    create_private_file(task_dir / "output.log")
    child = subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve()), "_worker", str(task_dir)],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
        close_fds=True,
        text=True,
    )
    if child.stdin is None:
        raise SystemExit("failed to open worker command channel")
    child.stdin.write(json.dumps(command, ensure_ascii=False))
    child.stdin.close()

    deadline = time.monotonic() + 5
    while not (task_dir / "worker.json").exists() and not (task_dir / "result.json").exists():
        if child.poll() is not None:
            shutil.rmtree(task_dir)
            raise SystemExit("worker exited before becoming ready")
        if time.monotonic() >= deadline:
            terminate_process_group(child)
            shutil.rmtree(task_dir)
            raise SystemExit(f"worker did not become ready: {task_dir}")
        time.sleep(0.02)
    print(json.dumps({"task_id": task_id, "task_dir": str(task_dir)}, ensure_ascii=False))
    return 0


def task_status(task_dir: Path) -> dict[str, Any]:
    metadata = read_json(task_dir / "metadata.json")
    result = stale_worker_result(task_dir)
    if (task_dir / "ack.json").exists():
        state = "acknowledged"
    elif result is not None:
        state = "completed"
    elif worker_holds_lock(task_dir):
        state = "running"
    else:
        state = "starting"
    value: dict[str, Any] = {
        "task_dir": str(task_dir),
        "task_id": metadata.get("task_id"),
        "thread_id": metadata.get("thread_id"),
        "name": metadata.get("name"),
        "state": state,
        "registered_at": metadata.get("registered_at"),
    }
    if result is not None:
        value.update(
            {
                "completed_at": result.get("completed_at"),
                "exit_code": result.get("exit_code"),
                "error": result.get("error"),
                "timed_out": result.get("timed_out", False),
            }
        )
    return value


def inspect_task(args: argparse.Namespace) -> int:
    task_dir = validate_task_dir(args.task_dir)
    value: dict[str, Any] = {"task_dir": str(task_dir), "status": task_status(task_dir)}
    for name in ("metadata.json", "worker.json", "result.json", "wake.json", "ack.json"):
        path = task_dir / name
        if path.exists():
            value[name.removesuffix(".json")] = read_json(path)
    print(json.dumps(value, ensure_ascii=False, indent=2))
    return 0


def list_tasks(args: argparse.Namespace) -> int:
    root = runtime_root() / thread_id()
    task_dirs = [child for child in root.iterdir() if (child / "metadata.json").is_file()] if root.is_dir() else []
    print(json.dumps([task_status(path) for path in sorted(task_dirs)], ensure_ascii=False, indent=2))
    return 0


def acknowledge(args: argparse.Namespace) -> int:
    task_dir = validate_task_dir(args.task_dir)
    if not (task_dir / "result.json").exists():
        raise SystemExit("cannot acknowledge an incomplete task")
    write_json_atomic(task_dir / "ack.json", {"acknowledged_at": now_iso()})
    print(json.dumps(task_status(task_dir), ensure_ascii=False))
    return 0


def clean(args: argparse.Namespace) -> int:
    task_dir = validate_task_dir(args.task_dir)
    if not (task_dir / "ack.json").exists():
        raise SystemExit("refusing to clean an unacknowledged task")
    shutil.rmtree(task_dir)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action", required=True)
    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("--name", required=True)
    start_parser.add_argument("--cwd", default=os.getcwd())
    start_parser.add_argument("--timeout", type=float)
    start_parser.add_argument("command", nargs=argparse.REMAINDER)
    worker_parser = subparsers.add_parser("_worker")
    worker_parser.add_argument("task_dir")
    for action in ("inspect", "status", "ack", "clean"):
        action_parser = subparsers.add_parser(action)
        action_parser.add_argument("--task-dir", required=True)
    subparsers.add_parser("list")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.action == "start":
        return start(args)
    if args.action == "_worker":
        return worker(validate_task_dir(args.task_dir))
    if args.action == "inspect":
        return inspect_task(args)
    if args.action == "status":
        print(json.dumps(task_status(validate_task_dir(args.task_dir)), ensure_ascii=False, indent=2))
        return 0
    if args.action == "list":
        return list_tasks(args)
    if args.action == "ack":
        return acknowledge(args)
    if args.action == "clean":
        return clean(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
