#!/usr/bin/env python3
"""Run one command, sample its observation contract, and persist durable events."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import time

from durable import append_event, atomic_write_json, locked_events, read_json, utc_now
from monitoring import MonitorEngine
from stages import StageObserver
from process_identity import ProcessIdentityError, require_process_identity


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-dir", required=True, type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        return 125
    target_umask = os.umask(0o077)
    atomic_write_json(args.job_dir / "process.json", require_process_identity())
    registration = read_json(args.job_dir / "job.json")
    stages = StageObserver(args.job_dir, registration)
    target_env = dict(os.environ)
    if registration.get("stage_path"):
        target_env["SUPERVISOR_JOB_ID"] = registration["job_id"]
        target_env["SUPERVISOR_STAGE_PATH"] = registration["stage_path"]
    else:
        target_env.pop("SUPERVISOR_STAGE_PATH", None)
        target_env.pop("SUPERVISOR_JOB_ID", None)
    worker_error = None
    pending_error = None
    try:
        target = subprocess.Popen(command, stdin=subprocess.DEVNULL, close_fds=True, env=target_env,
                                  **({"umask": target_umask} if os.name == "posix" else {}))
    except OSError as error:
        exit_code = 125
        worker_error = f"exec failed: {error}"
    else:
        engine = None
        try:
            target_identity = require_process_identity(target.pid)
        except (ProcessIdentityError, OSError) as error:
            # The child can finish before identity capture. Its Popen handle
            # still owns the exit status; never lose that result to a probe.
            if target.poll() is None:
                pending_error = f"target identity unavailable; health sampling disabled: {error}"[:1000]
                print(pending_error, file=sys.stderr, flush=True)
        else:
            try:
                atomic_write_json(args.job_dir / "target_process.json", target_identity)
                engine = MonitorEngine(args.job_dir, registration, target.pid)
            except Exception as error:
                pending_error = f"target monitor setup failed; health sampling disabled: {error}"[:1000]
                print(pending_error, file=sys.stderr, flush=True)
        wait_timeout = min(
            [2.0]
            + [float(monitor["sample_interval_seconds"]) for monitor in registration.get("monitors", [])]
        )
        reported_error = None
        while True:
            try:
                stages.tick()
                if engine is not None:
                    engine.tick()
            except Exception as error:  # preserve the target; surface monitor corruption once
                pending_error = f"worker monitor engine failed: {error}"[:1000]
                if pending_error != reported_error:
                    print(pending_error, file=sys.stderr, flush=True)
                    reported_error = pending_error
            if pending_error:
                try:
                    with locked_events(args.job_dir) as data:
                        if not any(event["event_type"] == "supervisor_error" for event in data["events"]):
                            append_event(data, registration, "supervisor_error", detail=pending_error)
                    pending_error = None
                except Exception:
                    # The diagnostic is already in the log. Preserve it for retry;
                    # inability to publish an event must not skip target.wait.
                    pass
            try:
                exit_code = target.wait(timeout=wait_timeout)
                try:
                    stages.tick()  # capture a final snapshot even for a short command
                except Exception as error:
                    pending_error = f"stage observation failed: {error}"[:1000]
                break
            except subprocess.TimeoutExpired:
                pass

    result = {"exit_code": exit_code, "finished_at": utc_now()}
    if worker_error:
        result["worker_error"] = worker_error[:1000]
    if pending_error:
        result["monitor_error"] = pending_error
    atomic_write_json(args.job_dir / "result.json", result)
    try:
        with locked_events(args.job_dir) as data:
            if pending_error and not any(event["event_type"] == "supervisor_error" for event in data["events"]):
                append_event(data, registration, "supervisor_error", detail=pending_error)
            if not any(event["event_type"] in ("completed", "failed") for event in data["events"]):
                append_event(
                    data,
                    registration,
                    "completed" if exit_code == 0 else "failed",
                    exit_code=exit_code,
                    finished_at=result["finished_at"],
                )
    except Exception as error:
        print(f"terminal result saved; event reconciliation deferred: {error}", file=sys.stderr, flush=True)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
