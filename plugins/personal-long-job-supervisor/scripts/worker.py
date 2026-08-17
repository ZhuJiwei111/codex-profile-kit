#!/usr/bin/env python3
"""Run one command, sample its observation contract, and persist durable events."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import time

from durable import append_event, atomic_write_json, locked_events, read_json, utc_now
from monitoring import MonitorEngine
from process_identity import require_process_identity


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-dir", required=True, type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        return 125
    os.umask(0o077)
    atomic_write_json(args.job_dir / "process.json", require_process_identity())
    registration = read_json(args.job_dir / "job.json")
    worker_error = None
    try:
        target = subprocess.Popen(command, stdin=subprocess.DEVNULL, close_fds=True)
        target_identity = require_process_identity(target.pid)
        atomic_write_json(args.job_dir / "target_process.json", target_identity)
        engine = MonitorEngine(args.job_dir, registration, target.pid)
        wait_timeout = min(
            [2.0]
            + [float(monitor["sample_interval_seconds"]) for monitor in registration.get("monitors", [])]
        )
        while True:
            try:
                engine.tick()
            except Exception as error:  # preserve the target; surface monitor corruption once
                with locked_events(args.job_dir) as data:
                    if not any(event["event_type"] == "supervisor_error" for event in data["events"]):
                        append_event(data, registration, "supervisor_error", detail=f"worker monitor engine failed: {error}"[:1000])
            try:
                exit_code = target.wait(timeout=wait_timeout)
                break
            except subprocess.TimeoutExpired:
                pass
    except OSError as error:
        exit_code = 125
        worker_error = f"exec failed: {error}"

    result = {"exit_code": exit_code, "finished_at": utc_now()}
    if worker_error:
        result["worker_error"] = worker_error[:1000]
    atomic_write_json(args.job_dir / "result.json", result)
    with locked_events(args.job_dir) as data:
        if not any(event["event_type"] in ("completed", "failed") for event in data["events"]):
            append_event(
                data,
                registration,
                "completed" if exit_code == 0 else "failed",
                exit_code=exit_code,
                finished_at=result["finished_at"],
            )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
