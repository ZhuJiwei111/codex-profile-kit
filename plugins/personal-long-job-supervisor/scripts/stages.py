"""Observe a task-owned current-stage snapshot in the existing worker loop."""
from __future__ import annotations

import json
import os
import stat
from pathlib import Path

from durable import append_event, locked_events


class StageObserver:
    def __init__(self, job_dir: Path, registration: dict):
        self.job_dir = job_dir
        self.registration = registration
        self.path = registration.get("stage_path")

    def tick(self):
        if not self.path:
            return
        snapshot, gap = None, None
        try:
            fd = os.open(self.path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0))
            with os.fdopen(fd, "rb") as handle:
                if not stat.S_ISREG(os.fstat(fd).st_mode):
                    raise ValueError("stage snapshot must be a regular file")
                raw = handle.read(8193)
            if len(raw) > 8192:
                raise ValueError("snapshot exceeds 8 KiB")
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError("snapshot must be an object")
            if value.get("job_id") != self.registration["job_id"]:
                raise ValueError("snapshot belongs to another job")
            seq, stage = value.get("seq"), value.get("stage")
            if type(seq) is not int or not 0 <= seq <= 2**53 - 1:
                raise ValueError("seq must be a nonnegative integer <= 2**53-1")
            if not isinstance(stage, str) or not stage.strip() or len(stage) > 160:
                raise ValueError("stage must be nonempty text, at most 160 characters")
            candidate = {"job_id": value["job_id"], "seq": seq, "stage": stage}
            for field in ("facts", "evidence"):
                if field in value:
                    if not isinstance(value[field], str) or len(value[field]) > 512:
                        raise ValueError(f"{field} must be text, at most 512 characters")
                    candidate[field] = value[field]
            snapshot = candidate
        except (OSError, ValueError, UnicodeError) as error:
            gap = str(error)[:256]
        with locked_events(self.job_dir) as data:
            state = data.setdefault("stage_state", {})
            previous = state.get("snapshot")
            if snapshot is not None:
                if previous is None or snapshot["seq"] > previous["seq"]:
                    state["snapshot"] = snapshot
                    append_event(data, self.registration, "stage_changed", stage=snapshot)
                elif snapshot["seq"] < previous["seq"]:
                    gap = "snapshot sequence is older than the last observed stage"
                elif snapshot != previous:
                    gap = "snapshot changed without increasing seq"
            state["evidence_gap"] = gap
