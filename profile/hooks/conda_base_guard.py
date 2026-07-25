#!/usr/bin/env python3
"""Deny explicit Conda install/create commands that target base."""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any


NAMED_BASE = re.compile(
    r"(?:^|[\s;&|])(?:conda|mamba)\s+(?:env\s+create|create|install)\b"
    r"[^;&|\n]*(?:-n|--name)(?:\s+|=)base(?:$|[\s;&|])",
    re.IGNORECASE,
)


def load_event() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"[conda-base-guard] invalid input JSON: {exc}", file=sys.stderr)
        return {}
    return value if isinstance(value, dict) else {}


def targets_base(command: str) -> bool:
    if NAMED_BASE.search(command):
        return True
    conda_root = os.environ.get("CONDA_ROOT")
    if not conda_root:
        return False
    prefix = re.escape(os.path.normpath(conda_root))
    return bool(
        re.search(
            rf"(?:^|[\s;&|])(?:conda|mamba)\s+(?:env\s+create|create|install)\b"
            rf"[^;&|\n]*(?:-p|--prefix)(?:\s+|=)[\"']?{prefix}[\"']?"
            rf"(?:$|[\s;&|])",
            command,
            re.IGNORECASE,
        )
    )


def emit_denial() -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        "[conda-base-policy] This install/create command targets "
                        "Conda base. Use the project environment or the "
                        "host-documented codex-tools environment."
                    ),
                }
            }
        )
    )


def main() -> int:
    event = load_event()
    tool_input = event.get("tool_input")
    if (
        event.get("hook_event_name") in {None, "PreToolUse"}
        and event.get("tool_name") == "Bash"
        and isinstance(tool_input, dict)
        and isinstance(tool_input.get("command"), str)
        and targets_base(tool_input["command"])
    ):
        emit_denial()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
