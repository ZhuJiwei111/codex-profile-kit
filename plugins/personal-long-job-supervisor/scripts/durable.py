"""Small durable-state primitives shared by the launcher, worker, and MCP server."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import time

if os.name == "nt":
    import msvcrt
else:
    import fcntl


RELEASE_VERSION = "0.6.10+codex.20261124"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def atomic_write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        if hasattr(os, "fchmod"):
            os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"invalid state file {path}: expected object")
    return value


def _lock_file(lock) -> None:
    if os.name == "nt":
        lock.seek(0, os.SEEK_END)
        if lock.tell() == 0:
            lock.write("\0")
            lock.flush()
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
    else:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)


def _unlock_file(lock) -> None:
    if os.name == "nt":
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


@contextmanager
def file_lock(lock_path: Path):
    with lock_path.open("a+", encoding="utf-8") as lock:
        os.chmod(lock_path, 0o600)
        _lock_file(lock)
        try:
            yield
        finally:
            _unlock_file(lock)


@contextmanager
def _file_locked_events(job_dir: Path):
    with file_lock(job_dir / "events.lock"):
        path = job_dir / "events.json"
        data = read_json(path)
        yield data
        atomic_write_json(path, data)


def append_event(data: dict, registration: dict, event_type: str, **fields) -> dict:
    event = {
        "event_id": int(data["next_event_id"]),
        "event_type": event_type,
        "job_id": registration["job_id"],
        "created_at": utc_now(),
        "acknowledged_at": None,
        **fields,
    }
    data["next_event_id"] = event["event_id"] + 1
    data["events"].append(event)
    return event


@contextmanager
def locked_events(job_dir: Path):
    registration = read_json(job_dir / "job.json") if (job_dir / "job.json").exists() else {}
    if registration.get("event_lock") != "mkdir":
        with _file_locked_events(job_dir) as data:
            yield data
        return
    from process_identity import execution_host_identity, require_process_identity
    lock = job_dir / "events.lockdir"
    deadline = time.monotonic() + 15
    while True:
        try:
            lock.mkdir(mode=0o700)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise RuntimeError(f"event lock busy: {lock}; verify its owner before recovery")
            time.sleep(0.05)
    try:
        atomic_write_json(lock / "owner.json", {"host": execution_host_identity(),
                                               "process": require_process_identity()})
        data = read_json(job_dir / "events.json")
        yield data
        atomic_write_json(job_dir / "events.json", data)
    finally:
        (lock / "owner.json").unlink(missing_ok=True)
        lock.rmdir()
