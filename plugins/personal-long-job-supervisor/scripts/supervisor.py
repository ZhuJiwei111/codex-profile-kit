#!/usr/bin/env python3
"""Durable, event-driven supervision for detached Linux processes."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid

from durable import append_event, atomic_write_json, locked_events, read_json, utc_now
from monitoring import MonitorError, NvidiaAdapter, discover_capabilities, normalize_monitors


SCHEMA_VERSION = 3
MAX_PAYLOAD_BYTES = 8192
DEFAULT_STATE_ROOT = Path.home() / ".local" / "state" / "personal-long-job-supervisor"
NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class SupervisorError(RuntimeError):
    pass


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
        return {"pid": pid, "start_ticks": int(fields[19]), "state_code": fields[0]}

    def start(self, registration: dict, worker_path: Path, python_executable: str) -> dict:
        command = [
            python_executable,
            str(worker_path),
            "--job-dir",
            registration["paths"]["job_dir"],
            "--",
            *registration.pop("_launch_command"),
        ]
        try:
            with open(registration["paths"]["log"], "ab", buffering=0) as log_handle:
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
                    identity = read_json(identity_path)
                    observed = self._identity(process.pid)
                    if (
                        int(identity.get("pid", -1)) != process.pid
                        or observed is None
                        or int(identity.get("start_ticks", -1)) != observed["start_ticks"]
                    ):
                        raise SupervisorError("detached worker identity did not verify")
                    return {"pid": process.pid, "start_ticks": observed["start_ticks"]}
                except (OSError, ValueError, json.JSONDecodeError) as error:
                    raise SupervisorError(f"invalid worker identity file: {error}") from error
            if process.poll() is not None:
                raise SupervisorError(f"detached worker {process.pid} exited before identity capture")
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
        state = "running" if active else ("exited" if observed is None or identity_matches else "identity_lost")
        return {
            "pid": pid,
            "start_ticks": start_ticks,
            "observed_start_ticks": observed_start,
            "identity_matches": identity_matches,
            "active": active,
            "state": state,
        }


class JobStore:
    def __init__(self, state_root: Path | str | None = None, runtime=None, nvidia_adapter=None):
        self.state_root = Path(state_root or os.environ.get("PLJS_STATE_ROOT", DEFAULT_STATE_ROOT)).resolve()
        self.jobs_root = self.state_root / "jobs"
        self.runtime = runtime or DetachedProcessRuntime()
        self.nvidia_adapter = nvidia_adapter or NvidiaAdapter()
        self._ensure_private_dir(self.state_root)
        self._ensure_private_dir(self.jobs_root)

    @staticmethod
    def _ensure_private_dir(path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True, mode=0o700)
        path.chmod(0o700)

    @staticmethod
    def _atomic_write_json(path: Path, value: dict) -> None:
        atomic_write_json(path, value)

    @staticmethod
    def _read_json(path: Path) -> dict:
        try:
            return read_json(path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            raise SupervisorError(f"invalid state file {path}: {error}") from error

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
            atomic_write_json(path, registration)
        return registration

    def start_job(
        self,
        *,
        name: str,
        cwd: Path | str,
        command: list[str],
        monitors: list[str | dict] | None = None,
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
        raw_monitors = list(monitors or [])
        if heartbeat_path is not None:
            try:
                kinds = [
                    (json.loads(item) if isinstance(item, str) else item).get("kind")
                    for item in raw_monitors
                ]
            except (json.JSONDecodeError, AttributeError, TypeError) as error:
                raise SupervisorError(f"monitor must be a JSON object: {error}") from error
            if "heartbeat_stale" in kinds:
                raise SupervisorError("heartbeat compatibility flags conflict with heartbeat_stale monitor")
            raw_monitors.append(
                {
                    "kind": "heartbeat_stale",
                    "path": str(heartbeat_path),
                    "stale_after_seconds": stale_after,
                    "sample_interval_seconds": min(5.0, max(0.05, float(stale_after) / 2)),
                }
            )
        try:
            normalized_monitors = normalize_monitors(raw_monitors, cwd_path, self.nvidia_adapter)
        except (MonitorError, json.JSONDecodeError, AttributeError) as error:
            raise SupervisorError(str(error)) from error

        job_id = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:12]}"
        job_dir = self.job_dir(job_id)
        job_dir.mkdir(mode=0o700)
        log_path = job_dir / "combined.log"
        log_path.touch(mode=0o600)
        artifact_paths = [str(Path(item).expanduser().resolve()) for item in (artifacts or [])]
        python_executable = str(Path(sys.executable).resolve())
        created_at = utc_now()
        registration = {
            "schema_version": SCHEMA_VERSION,
            "job_id": job_id,
            "name": name,
            "cwd": str(cwd_path),
            "created_at": created_at,
            "created_epoch": parse_time(created_at),
            "executable": Path(command[0]).name,
            "argument_count": len(command),
            "monitors": normalized_monitors,
            "artifacts": artifact_paths,
            "python_executable": python_executable,
            "supervisor_path": str(Path(__file__).resolve()),
            "paths": {
                "job_dir": str(job_dir),
                "log": str(log_path),
                "identity": str(job_dir / "process.json"),
                "target_identity": str(job_dir / "target_process.json"),
                "result": str(job_dir / "result.json"),
            },
        }
        atomic_write_json(job_dir / "job.json", registration)
        atomic_write_json(
            job_dir / "events.json",
            {"schema_version": SCHEMA_VERSION, "next_event_id": 1, "events": [], "conditions": {}, "monitor_states": {}},
        )
        launch_registration = dict(registration)
        launch_registration["_launch_command"] = list(command)
        try:
            registration["process"] = self.runtime.start(
                launch_registration, Path(__file__).with_name("worker.py").resolve(), python_executable
            )
            atomic_write_json(job_dir / "job.json", registration)
        except Exception as error:
            self._record_supervisor_error(job_id, f"launch failed: {error}", registration)
            raise SupervisorError(f"launch failed for registered job {job_id}: {error}") from error
        return self.inspect_job(job_id)

    @contextmanager
    def _locked_events(self, job_id: str):
        try:
            with locked_events(self.job_dir(job_id)) as data:
                yield data
        except FileNotFoundError as error:
            raise SupervisorError(f"unknown job: {job_id}") from error

    def _record_supervisor_error(self, job_id: str, message: str, registration=None) -> None:
        registration = registration or self._registration(job_id)
        with self._locked_events(job_id) as data:
            if not any(event["event_type"] == "supervisor_error" for event in data["events"]):
                append_event(data, registration, "supervisor_error", detail=message[:1000])

    def _reconcile_v2_heartbeat(self, registration: dict, data: dict, result) -> None:
        heartbeat = registration.get("heartbeat_path")
        stale_after = registration.get("stale_after_seconds")
        if result is not None or not heartbeat or not stale_after:
            return
        try:
            age = max(0.0, time.time() - Path(heartbeat).stat().st_mtime)
        except FileNotFoundError:
            age = max(0.0, time.time() - parse_time(registration["created_at"]))
        stale = age >= float(stale_after)
        active = bool(data.setdefault("conditions", {}).get("heartbeat_stale"))
        if stale and not active:
            append_event(data, registration, "attention", reason="heartbeat_stale", heartbeat_age_seconds=round(age, 3))
        data["conditions"]["heartbeat_stale"] = stale

    def _reconcile(self, job_id: str) -> tuple[dict, dict, dict]:
        registration = self._registration(job_id)
        process_state = self.runtime.inspect(registration["process"])
        result_path = self.job_dir(job_id) / "result.json"
        result = self._read_json(result_path) if result_path.exists() else None
        with self._locked_events(job_id) as data:
            if result is not None and not any(event["event_type"] in ("completed", "failed") for event in data["events"]):
                exit_code = int(result["exit_code"])
                append_event(data, registration, "completed" if exit_code == 0 else "failed", exit_code=exit_code, finished_at=result.get("finished_at"))
            if int(registration.get("schema_version", 2)) == 2:
                self._reconcile_v2_heartbeat(registration, data, result)
            if result is None and not process_state["active"]:
                age = time.time() - parse_time(registration["created_at"])
                if age >= 2 and not any(event["event_type"] == "supervisor_error" for event in data["events"]):
                    detail = "process identity was lost without a result record" if process_state["state"] == "identity_lost" else "detached worker exited without a result record"
                    append_event(data, registration, "supervisor_error", detail=detail)
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
            "reason": event.get("reason"),
            "monitor_id": event.get("monitor_id"),
            "scope": event.get("scope"),
            "subject": event.get("subject"),
            "condition_since": event.get("condition_since"),
            "detail": event.get("detail"),
            "evidence": event.get("evidence"),
            "evidence_gap": event.get("evidence_gap"),
            "process": registration["process"],
            "target_process": self._target_identity(registration),
            "process_state": process_state,
            "paths": {"job_dir": registration["paths"]["job_dir"], "log": registration["paths"]["log"], "result": registration["paths"]["result"], "artifacts": registration.get("artifacts", [])[:16]},
            "commands": {"inspect": f"{command} status {registration['job_id']}", "ack": f"{command} ack {registration['job_id']} {event['event_id']}"},
            "authority": event.get("authority") or "observe_only; do not cancel, retry, restart, reconfigure, or launch a next stage",
        }
        return self._bounded(view)

    def _target_identity(self, registration: dict) -> dict | None:
        path = registration.get("paths", {}).get("target_identity")
        if not path or not Path(path).exists():
            return None
        try:
            return self._read_json(Path(path))
        except SupervisorError:
            return None

    @staticmethod
    def _bounded(value: dict) -> dict:
        candidate = json.loads(json.dumps(value, ensure_ascii=False))
        if len(json.dumps(candidate, ensure_ascii=False, separators=(",", ":")).encode()) <= MAX_PAYLOAD_BYTES:
            return candidate
        if isinstance(candidate.get("artifacts"), list):
            candidate["artifacts"] = [str(item)[:256] for item in candidate["artifacts"][:4]]
        if isinstance(candidate.get("paths"), dict):
            candidate["paths"]["artifacts"] = [str(item)[:256] for item in candidate["paths"].get("artifacts", [])[:4]]
        if isinstance(candidate.get("monitor_states"), dict):
            candidate["monitor_states"] = dict(list(candidate["monitor_states"].items())[:4])
        if isinstance(candidate.get("pending_event"), dict):
            candidate["pending_event"] = JobStore._bounded(candidate["pending_event"])
        for field in ("detail", "evidence_gap"):
            if candidate.get(field):
                candidate[field] = str(candidate[field])[:512]
        encoded = json.dumps(candidate, ensure_ascii=False, separators=(",", ":")).encode()
        if len(encoded) <= MAX_PAYLOAD_BYTES:
            candidate["payload_truncated"] = True
            return candidate
        compact = {key: candidate.get(key) for key in ("job_id", "name", "status", "event_id", "event_type", "exit_code", "event_time", "reason", "monitor_id", "scope", "subject", "process", "target_process", "process_state", "commands", "authority") if key in candidate}
        compact["paths"] = candidate.get("paths", {})
        compact["payload_truncated"] = True
        return compact

    def render_payload(self, value: dict) -> str:
        payload = json.dumps(self._bounded(value), ensure_ascii=False, separators=(",", ":"))
        if len(payload.encode()) > MAX_PAYLOAD_BYTES:
            raise SupervisorError("bounded payload invariant violated")
        return payload

    def inspect_job(self, job_id: str) -> dict:
        registration, data, process_state = self._reconcile(job_id)
        pending = next((event for event in data["events"] if not event.get("acknowledged_at")), None)
        terminal = next((event for event in reversed(data["events"]) if event["event_type"] in ("completed", "failed")), None)
        status = terminal["event_type"] if terminal else ("running" if process_state["active"] else process_state["state"])
        return self._bounded(
            {
                "job_id": job_id,
                "name": registration["name"],
                "schema_version": registration.get("schema_version", 2),
                "status": status,
                "process": registration["process"],
                "target_process": self._target_identity(registration),
                "process_state": process_state,
                "pending_event": self._event_view(pending, registration, process_state) if pending else None,
                "paths": registration["paths"],
                "monitors": registration.get("monitors", []),
                "monitor_states": data.get("monitor_states", {}),
                "heartbeat_path": registration.get("heartbeat_path"),
                "stale_after_seconds": registration.get("stale_after_seconds"),
                "artifacts": registration.get("artifacts", [])[:16],
            }
        )

    def wait_event(self, job_id: str, poll_interval: float = 2.0, cancel_event=None) -> dict:
        while True:
            observed = self.inspect_job(job_id)
            if observed["pending_event"]:
                return observed["pending_event"]
            if observed["status"] in ("completed", "failed"):
                raise SupervisorError(f"job {job_id} is already terminal and has no unacknowledged event")
            if cancel_event is not None:
                if cancel_event.wait(poll_interval):
                    raise SupervisorError("wait cancelled by MCP client; underlying job is unchanged")
            else:
                time.sleep(poll_interval)

    def ack_event(self, job_id: str, event_id: int) -> dict:
        self._registration(job_id)
        with self._locked_events(job_id) as data:
            event = next((item for item in data["events"] if int(item["event_id"]) == int(event_id)), None)
            if event is None:
                raise SupervisorError(f"unknown event_id {event_id} for job {job_id}")
            already = bool(event.get("acknowledged_at"))
            if not already:
                event["acknowledged_at"] = utc_now()
            return {"job_id": job_id, "event_id": int(event_id), "acknowledged": True, "already_acknowledged": already}

    def list_jobs(self) -> dict:
        jobs, skipped = [], 0
        for path in sorted(self.jobs_root.iterdir(), reverse=True):
            if not path.is_dir():
                continue
            try:
                observed = self.inspect_job(path.name)
                pending = observed.get("pending_event")
                jobs.append({"job_id": observed["job_id"], "name": observed["name"], "status": observed["status"], "process": observed["process"], "pending_event": ({key: pending.get(key) for key in ("event_id", "event_type", "event_time", "exit_code", "reason")} if pending else None), "job_dir": observed["paths"]["job_dir"]})
            except SupervisorError:
                skipped += 1
        bounded = []
        for job in jobs[:100]:
            candidate = {"jobs": bounded + [job], "total_jobs": len(jobs), "truncated": len(bounded) + 1 < len(jobs), "skipped_corrupt": skipped}
            if len(json.dumps(candidate, ensure_ascii=False, separators=(",", ":")).encode()) > 7800:
                break
            bounded.append(job)
        return {"jobs": bounded, "total_jobs": len(jobs), "truncated": len(bounded) < len(jobs), "skipped_corrupt": skipped}

    def clean_job(self, job_id: str) -> dict:
        observed = self.inspect_job(job_id)
        if observed["process_state"]["active"]:
            raise SupervisorError("refusing to clean a running job")
        if observed["pending_event"] is not None:
            raise SupervisorError("acknowledge all events before cleaning the job")
        events = self._read_json(self.job_dir(job_id) / "events.json")["events"]
        if not any(event.get("event_type") in ("completed", "failed", "supervisor_error") and event.get("acknowledged_at") for event in events):
            raise SupervisorError("refusing to clean without a confirmed terminal event")
        shutil.rmtree(self.job_dir(job_id))
        return {"job_id": job_id, "cleaned": True}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Supervise detached long-running processes")
    parser.add_argument("--state-root", type=Path, help=argparse.SUPPRESS)
    commands = parser.add_subparsers(dest="subcommand", required=True)
    start = commands.add_parser("start", help="start a command in a detached process session")
    start.add_argument("--name", required=True)
    start.add_argument("--cwd", required=True, type=Path)
    start.add_argument("--monitor", action="append", default=[])
    start.add_argument("--heartbeat-path", type=Path)
    start.add_argument("--stale-after", type=float)
    start.add_argument("--artifact", action="append", default=[], type=Path)
    start.add_argument("command", nargs=argparse.REMAINDER)
    status = commands.add_parser("status", help="inspect one job")
    status.add_argument("job_id")
    commands.add_parser("list", help="list registered jobs")
    commands.add_parser("capabilities", help="discover read-only monitor capabilities")
    ack = commands.add_parser("ack", help="acknowledge one event")
    ack.add_argument("job_id")
    ack.add_argument("event_id", type=int)
    clean = commands.add_parser("clean", help="remove an acknowledged inactive job record")
    clean.add_argument("job_id")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.subcommand == "capabilities":
            output = discover_capabilities()
            print(json.dumps(output, ensure_ascii=False, separators=(",", ":")))
            return 0
        store = JobStore(args.state_root)
        if args.subcommand == "start":
            command = args.command[1:] if args.command and args.command[0] == "--" else args.command
            output = store.start_job(name=args.name, cwd=args.cwd, command=command, monitors=args.monitor, heartbeat_path=args.heartbeat_path, stale_after=args.stale_after, artifacts=args.artifact)
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
    except (SupervisorError, MonitorError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
