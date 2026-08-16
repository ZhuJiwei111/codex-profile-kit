#!/usr/bin/env python3
"""Event-driven supervision for detached long-running processes."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid


SCHEMA_VERSION = 2
MAX_PAYLOAD_BYTES = 8192
DEFAULT_STATE_ROOT = Path.home() / ".local" / "state" / "personal-long-job-supervisor"
NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class SupervisorError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_time(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


class DetachedProcessRuntime:
    def __init__(self):
        self._children: dict[int, subprocess.Popen] = {}

    @staticmethod
    def _identity(pid: int) -> dict | None:
        try:
            raw = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
        except FileNotFoundError:
            return None
        except OSError as error:
            raise SupervisorError(f"cannot inspect process {pid}: {error}") from error
        _, separator, tail = raw.rpartition(")")
        fields = tail.strip().split() if separator else []
        if len(fields) < 20:
            raise SupervisorError(f"invalid /proc identity for process {pid}")
        return {
            "pid": pid,
            "start_ticks": int(fields[19]),
            "state_code": fields[0],
        }

    def start(self, registration: dict, worker_path: Path, python_executable: str) -> dict:
        command = [
            python_executable,
            str(worker_path),
            "--job-dir",
            registration["paths"]["job_dir"],
            "--",
            *registration.pop("_launch_command"),
        ]
        log_path = registration["paths"]["log"]
        try:
            with open(log_path, "ab", buffering=0) as log_handle:
                process = subprocess.Popen(
                    command,
                    cwd=registration["cwd"],
                    stdin=subprocess.DEVNULL,
                    stdout=log_handle,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                    close_fds=True,
                )
        except OSError as error:
            raise SupervisorError(f"detached launch failed: {error}") from error
        self._children[process.pid] = process
        identity_path = Path(registration["paths"]["identity"])
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            if identity_path.exists():
                try:
                    identity = json.loads(identity_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as error:
                    raise SupervisorError(f"invalid worker identity file: {error}") from error
                observed = self._identity(process.pid)
                if (
                    not isinstance(identity, dict)
                    or int(identity.get("pid", -1)) != process.pid
                    or observed is None
                    or int(identity.get("start_ticks", -1)) != observed["start_ticks"]
                ):
                    raise SupervisorError("detached worker identity did not verify")
                return {
                    "pid": process.pid,
                    "start_ticks": observed["start_ticks"],
                }
            if process.poll() is not None:
                raise SupervisorError(
                    f"detached worker {process.pid} exited before identity capture"
                )
            time.sleep(0.01)
        raise SupervisorError(f"timed out waiting for detached worker {process.pid} identity")

    def inspect(self, expected: dict) -> dict:
        pid = int(expected["pid"])
        start_ticks = int(expected["start_ticks"])
        child = self._children.get(pid)
        if child is not None and child.poll() is not None:
            self._children.pop(pid, None)
        observed = self._identity(pid)
        observed_start = observed["start_ticks"] if observed else None
        identity_matches = observed_start == start_ticks
        active = bool(identity_matches and observed["state_code"] not in ("X", "Z"))
        if active:
            state = "running"
        elif observed is None:
            state = "exited"
        elif not identity_matches:
            state = "identity_lost"
        else:
            state = "exited"
        return {
            "pid": pid,
            "start_ticks": start_ticks,
            "observed_start_ticks": observed_start,
            "identity_matches": identity_matches,
            "active": active,
            "state": state,
        }

class JobStore:
    def __init__(self, state_root: Path | str | None = None, runtime=None):
        self.state_root = Path(state_root or os.environ.get("PLJS_STATE_ROOT", DEFAULT_STATE_ROOT)).resolve()
        self.jobs_root = self.state_root / "jobs"
        self.runtime = runtime or DetachedProcessRuntime()
        self._ensure_private_dir(self.state_root)
        self._ensure_private_dir(self.jobs_root)

    @staticmethod
    def _ensure_private_dir(path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True, mode=0o700)
        path.chmod(0o700)

    @staticmethod
    def _atomic_write_json(path: Path, value: dict) -> None:
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

    @staticmethod
    def _read_json(path: Path) -> dict:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise SupervisorError(f"invalid state file {path}: {error}") from error
        if not isinstance(value, dict):
            raise SupervisorError(f"invalid state file {path}: expected object")
        return value

    def job_dir(self, job_id: str) -> Path:
        if not re.fullmatch(r"[a-z0-9-]{8,80}", job_id):
            raise SupervisorError("invalid job_id")
        path = (self.jobs_root / job_id).resolve()
        if path.parent != self.jobs_root:
            raise SupervisorError("invalid job_id")
        return path

    def _registration(self, job_id: str) -> dict:
        job_dir = self.job_dir(job_id)
        path = job_dir / "job.json"
        registration = self._read_json(path)
        if "process" not in registration:
            identity_path = job_dir / "process.json"
            if not identity_path.exists():
                raise SupervisorError(f"process identity is not yet available for job {job_id}")
            identity = self._read_json(identity_path)
            try:
                registration["process"] = {
                    "pid": int(identity["pid"]),
                    "start_ticks": int(identity["start_ticks"]),
                }
            except (KeyError, TypeError, ValueError) as error:
                raise SupervisorError(f"invalid process identity for job {job_id}") from error
            self._atomic_write_json(path, registration)
        return registration

    def start_job(
        self,
        *,
        name: str,
        cwd: Path | str,
        command: list[str],
        heartbeat_path: Path | str | None = None,
        stale_after: float | None = None,
        artifacts: list[Path | str] | None = None,
    ) -> dict:
        if not NAME_PATTERN.fullmatch(name):
            raise SupervisorError("name must be 1-64 characters using letters, digits, '.', '_' or '-'")
        cwd_path = Path(cwd).expanduser().resolve()
        if not cwd_path.is_dir():
            raise SupervisorError(f"cwd is not a directory: {cwd_path}")
        if not command or not command[0]:
            raise SupervisorError("COMMAND is required")
        if any("\x00" in argument or "\n" in argument for argument in command):
            raise SupervisorError("command arguments may not contain NUL or newline")
        if (heartbeat_path is None) != (stale_after is None):
            raise SupervisorError("--heartbeat-path and --stale-after must be used together")
        if stale_after is not None and stale_after <= 0:
            raise SupervisorError("stale-after must be greater than zero")

        job_id = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:12]}"
        job_dir = self.job_dir(job_id)
        job_dir.mkdir(mode=0o700)
        job_dir.chmod(0o700)
        log_path = job_dir / "combined.log"
        log_path.touch(mode=0o600)
        log_path.chmod(0o600)
        artifact_paths = [str(Path(item).expanduser().resolve()) for item in (artifacts or [])]
        heartbeat = str(Path(heartbeat_path).expanduser().resolve()) if heartbeat_path else None
        python_executable = str(Path(sys.executable).resolve())
        worker_path = Path(__file__).with_name("worker.py").resolve()
        registration = {
            "schema_version": SCHEMA_VERSION,
            "job_id": job_id,
            "name": name,
            "cwd": str(cwd_path),
            "created_at": utc_now(),
            "executable": Path(command[0]).name,
            "argument_count": len(command),
            "heartbeat_path": heartbeat,
            "stale_after_seconds": stale_after,
            "artifacts": artifact_paths,
            "python_executable": python_executable,
            "supervisor_path": str(Path(__file__).resolve()),
            "paths": {
                "job_dir": str(job_dir),
                "log": str(log_path),
                "identity": str(job_dir / "process.json"),
                "result": str(job_dir / "result.json"),
            },
        }
        self._atomic_write_json(job_dir / "job.json", registration)
        self._atomic_write_json(
            job_dir / "events.json",
            {"schema_version": SCHEMA_VERSION, "next_event_id": 1, "events": [], "conditions": {}},
        )
        launch_registration = dict(registration)
        launch_registration["_launch_command"] = list(command)
        try:
            registration["process"] = self.runtime.start(
                launch_registration, worker_path, python_executable
            )
            self._atomic_write_json(job_dir / "job.json", registration)
        except Exception as error:
            self._record_supervisor_error(
                job_id, f"launch failed: {error}", registration=registration
            )
            raise SupervisorError(f"launch failed for registered job {job_id}: {error}") from error
        return self.inspect_job(job_id)

    @contextmanager
    def _locked_events(self, job_id: str):
        job_dir = self.job_dir(job_id)
        lock_path = job_dir / "events.lock"
        try:
            with lock_path.open("a+", encoding="utf-8") as lock:
                os.chmod(lock_path, 0o600)
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
                events_path = job_dir / "events.json"
                data = self._read_json(events_path)
                yield data
                self._atomic_write_json(events_path, data)
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        except FileNotFoundError as error:
            raise SupervisorError(f"unknown job: {job_id}") from error

    @staticmethod
    def _new_event(data: dict, registration: dict, event_type: str, **fields) -> dict:
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

    def _record_supervisor_error(
        self, job_id: str, message: str, registration: dict | None = None
    ) -> None:
        registration = registration or self._registration(job_id)
        with self._locked_events(job_id) as data:
            if not any(event["event_type"] == "supervisor_error" for event in data["events"]):
                self._new_event(data, registration, "supervisor_error", detail=message[:1000])

    def _reconcile(self, job_id: str) -> tuple[dict, dict, dict]:
        registration = self._registration(job_id)
        process_state = self.runtime.inspect(registration["process"])
        result_path = self.job_dir(job_id) / "result.json"
        result = self._read_json(result_path) if result_path.exists() else None
        with self._locked_events(job_id) as data:
            if result is not None and not any(
                event["event_type"] in ("completed", "failed") for event in data["events"]
            ):
                exit_code = int(result["exit_code"])
                self._new_event(
                    data,
                    registration,
                    "completed" if exit_code == 0 else "failed",
                    exit_code=exit_code,
                    finished_at=result.get("finished_at"),
                )

            heartbeat_age = None
            heartbeat_path = registration.get("heartbeat_path")
            stale_after = registration.get("stale_after_seconds")
            if result is None and heartbeat_path and stale_after:
                try:
                    heartbeat_age = max(0.0, time.time() - Path(heartbeat_path).stat().st_mtime)
                except FileNotFoundError:
                    heartbeat_age = max(0.0, time.time() - parse_time(registration["created_at"]))
                stale = heartbeat_age >= float(stale_after)
                active = bool(data["conditions"].get("heartbeat_stale"))
                if stale and not active:
                    self._new_event(
                        data,
                        registration,
                        "attention",
                        heartbeat_age_seconds=round(heartbeat_age, 3),
                        reason="heartbeat_stale",
                    )
                data["conditions"]["heartbeat_stale"] = stale

            if result is None and not process_state["active"]:
                age = time.time() - parse_time(registration["created_at"])
                if age >= 2 and not any(event["event_type"] == "supervisor_error" for event in data["events"]):
                    self._new_event(
                        data,
                        registration,
                        "supervisor_error",
                        detail=(
                            "process identity was lost without a result record"
                            if process_state["state"] == "identity_lost"
                            else "detached worker exited without a result record"
                        ),
                    )
            return registration, data, process_state

    def _event_view(self, event: dict, registration: dict, process_state: dict) -> dict:
        command = f"{registration['python_executable']} {registration['supervisor_path']}"
        view = {
            "job_id": registration["job_id"],
            "name": registration["name"],
            "event_id": event["event_id"],
            "event_type": event["event_type"],
            "exit_code": event.get("exit_code"),
            "event_time": event["created_at"],
            "finished_at": event.get("finished_at"),
            "heartbeat_age_seconds": event.get("heartbeat_age_seconds"),
            "reason": event.get("reason"),
            "detail": event.get("detail"),
            "process": registration["process"],
            "process_state": process_state,
            "paths": {
                "job_dir": registration["paths"]["job_dir"],
                "log": registration["paths"]["log"],
                "result": registration["paths"]["result"],
                "heartbeat": registration.get("heartbeat_path"),
                "artifacts": registration.get("artifacts", [])[:16],
            },
            "commands": {
                "inspect": f"{command} status {registration['job_id']}",
                "ack": f"{command} ack {registration['job_id']} {event['event_id']}",
            },
            "authority": "observe_only; do not cancel, retry, restart, reconfigure, or launch a next stage",
        }
        return self._bounded(view)

    @staticmethod
    def _bounded(value: dict) -> dict:
        encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if len(encoded) <= MAX_PAYLOAD_BYTES:
            return value
        paths = value.get("paths", {})
        if isinstance(paths, dict):
            paths["artifacts"] = paths.get("artifacts", [])[:4]
        if isinstance(value.get("artifacts"), list):
            value["artifacts"] = [str(item)[:256] for item in value["artifacts"][:4]]
        if isinstance(value.get("pending_event"), dict):
            value["pending_event"] = JobStore._bounded(value["pending_event"])
        if value.get("detail"):
            value["detail"] = str(value["detail"])[:512]
        encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if len(encoded) <= MAX_PAYLOAD_BYTES:
            return value
        for section in ("paths", "commands"):
            for key, item in list(value.get(section, {}).items()):
                if isinstance(item, str) and len(item) > 256:
                    value[section][key] = item[:253] + "..."
                elif isinstance(item, list):
                    value[section][key] = [str(entry)[:256] for entry in item[:2]]
        value["payload_truncated"] = True
        encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if len(encoded) <= MAX_PAYLOAD_BYTES:
            return value
        compact = {
            key: value.get(key)
            for key in (
                "job_id",
                "name",
                "status",
                "event_id",
                "event_type",
                "exit_code",
                "event_time",
                "reason",
                "heartbeat_age_seconds",
                "process",
                "process_state",
                "commands",
                "authority",
            )
            if key in value
        }
        compact["paths"] = value.get("paths", {})
        compact["payload_truncated"] = True
        return compact

    def render_payload(self, value: dict) -> str:
        bounded = self._bounded(value)
        payload = json.dumps(bounded, ensure_ascii=False, separators=(",", ":"))
        if len(payload.encode("utf-8")) > MAX_PAYLOAD_BYTES:
            raise SupervisorError("bounded payload invariant violated")
        return payload

    def inspect_job(self, job_id: str) -> dict:
        registration, data, process_state = self._reconcile(job_id)
        pending = next((event for event in data["events"] if not event.get("acknowledged_at")), None)
        terminal = next(
            (event for event in reversed(data["events"]) if event["event_type"] in ("completed", "failed")),
            None,
        )
        if terminal:
            status = terminal["event_type"]
        elif process_state["active"]:
            status = "running"
        else:
            status = process_state["state"]
        result = {
            "job_id": job_id,
            "name": registration["name"],
            "status": status,
            "process": registration["process"],
            "process_state": process_state,
            "pending_event": self._event_view(pending, registration, process_state) if pending else None,
            "paths": registration["paths"],
            "heartbeat_path": registration.get("heartbeat_path"),
            "stale_after_seconds": registration.get("stale_after_seconds"),
            "artifacts": registration.get("artifacts", [])[:16],
        }
        return self._bounded(result)

    def wait_event(self, job_id: str, poll_interval: float = 2.0, cancel_event=None) -> dict:
        while True:
            observed = self.inspect_job(job_id)
            if observed["pending_event"]:
                return observed["pending_event"]
            if observed["status"] in ("completed", "failed"):
                raise SupervisorError(
                    f"job {job_id} is already terminal and has no unacknowledged event"
                )
            if cancel_event is not None:
                if cancel_event.wait(poll_interval):
                    raise SupervisorError("wait cancelled by MCP client; underlying job is unchanged")
            else:
                time.sleep(poll_interval)

    def ack_event(self, job_id: str, event_id: int) -> dict:
        registration = self._registration(job_id)
        del registration
        with self._locked_events(job_id) as data:
            event = next((item for item in data["events"] if int(item["event_id"]) == int(event_id)), None)
            if event is None:
                raise SupervisorError(f"unknown event_id {event_id} for job {job_id}")
            already = bool(event.get("acknowledged_at"))
            if not already:
                event["acknowledged_at"] = utc_now()
            return {
                "job_id": job_id,
                "event_id": int(event_id),
                "acknowledged": True,
                "already_acknowledged": already,
            }

    def list_jobs(self) -> dict:
        jobs = []
        skipped = 0
        if not self.jobs_root.exists():
            return {"jobs": [], "skipped_corrupt": 0}
        for path in sorted(self.jobs_root.iterdir(), reverse=True):
            if not path.is_dir():
                continue
            try:
                observed = self.inspect_job(path.name)
                pending = observed.get("pending_event")
                jobs.append(
                    {
                        "job_id": observed["job_id"],
                        "name": observed["name"],
                        "status": observed["status"],
                        "process": observed["process"],
                        "pending_event": (
                            {
                                "event_id": pending["event_id"],
                                "event_type": pending["event_type"],
                                "event_time": pending["event_time"],
                                "exit_code": pending.get("exit_code"),
                            }
                            if pending
                            else None
                        ),
                        "job_dir": observed["paths"]["job_dir"],
                    }
                )
            except SupervisorError:
                skipped += 1
        bounded_jobs = []
        for job in jobs[:100]:
            candidate = {
                "jobs": bounded_jobs + [job],
                "total_jobs": len(jobs),
                "truncated": len(bounded_jobs) + 1 < len(jobs),
                "skipped_corrupt": skipped,
            }
            if len(json.dumps(candidate, ensure_ascii=False, separators=(",", ":")).encode("utf-8")) > 7800:
                break
            bounded_jobs.append(job)
        return {
            "jobs": bounded_jobs,
            "total_jobs": len(jobs),
            "truncated": len(bounded_jobs) < len(jobs),
            "skipped_corrupt": skipped,
        }

    def clean_job(self, job_id: str) -> dict:
        observed = self.inspect_job(job_id)
        if observed["process_state"]["active"]:
            raise SupervisorError("refusing to clean a running job")
        if observed["pending_event"] is not None:
            raise SupervisorError("acknowledge all events before cleaning the job")
        events = self._read_json(self.job_dir(job_id) / "events.json")["events"]
        if not any(
            event.get("event_type") in ("completed", "failed", "supervisor_error")
            and event.get("acknowledged_at")
            for event in events
        ):
            raise SupervisorError("refusing to clean without a confirmed terminal event")
        path = self.job_dir(job_id)
        shutil.rmtree(path)
        return {"job_id": job_id, "cleaned": True}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Supervise detached long-running processes")
    parser.add_argument("--state-root", type=Path, help=argparse.SUPPRESS)
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    start = subparsers.add_parser("start", help="start a command in a transient user service")
    start.add_argument("--name", required=True)
    start.add_argument("--cwd", required=True, type=Path)
    start.add_argument("--heartbeat-path", type=Path)
    start.add_argument("--stale-after", type=float)
    start.add_argument("--artifact", action="append", default=[], type=Path)
    start.add_argument("command", nargs=argparse.REMAINDER)

    status = subparsers.add_parser("status", help="inspect one job")
    status.add_argument("job_id")
    subparsers.add_parser("list", help="list registered jobs")
    ack = subparsers.add_parser("ack", help="acknowledge one event")
    ack.add_argument("job_id")
    ack.add_argument("event_id", type=int)
    clean = subparsers.add_parser("clean", help="remove an acknowledged inactive job record")
    clean.add_argument("job_id")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    store = JobStore(args.state_root)
    try:
        if args.subcommand == "start":
            command = args.command[1:] if args.command and args.command[0] == "--" else args.command
            output = store.start_job(
                name=args.name,
                cwd=args.cwd,
                command=command,
                heartbeat_path=args.heartbeat_path,
                stale_after=args.stale_after,
                artifacts=args.artifact,
            )
        elif args.subcommand == "status":
            output = store.inspect_job(args.job_id)
        elif args.subcommand == "list":
            output = store.list_jobs()
        elif args.subcommand == "ack":
            output = store.ack_event(args.job_id, args.event_id)
        elif args.subcommand == "clean":
            output = store.clean_job(args.job_id)
        else:
            parser.error("unknown command")
            return 2
        print(store.render_payload(output))
        return 0
    except SupervisorError as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
