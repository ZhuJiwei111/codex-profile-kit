"""Small durable-state primitives shared by the launcher, worker, and MCP server."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import tempfile


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def atomic_write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
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


@contextmanager
def locked_events(job_dir: Path):
    lock_path = job_dir / "events.lock"
    with lock_path.open("a+", encoding="utf-8") as lock:
        os.chmod(lock_path, 0o600)
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        path = job_dir / "events.json"
        data = read_json(path)
        yield data
        atomic_write_json(path, data)
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


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
