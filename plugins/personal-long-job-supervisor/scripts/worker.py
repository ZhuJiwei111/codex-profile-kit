#!/usr/bin/env python3
"""Run one registered command and atomically record its exit status."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


def atomic_write(path: Path, value: dict) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True, separators=(",", ":"))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-dir", required=True, type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        return 125
    os.umask(0o077)
    try:
        exit_code = subprocess.run(command, check=False).returncode
        worker_error = None
    except OSError as error:
        exit_code = 125
        worker_error = f"exec failed: {error}"
    result = {
        "exit_code": exit_code,
        "finished_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if worker_error:
        result["worker_error"] = worker_error[:1000]
    atomic_write(args.job_dir / "result.json", result)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
