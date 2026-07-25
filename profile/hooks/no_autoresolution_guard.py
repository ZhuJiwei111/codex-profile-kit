#!/usr/bin/env python3
"""Deny user-input requests that include an automatic-resolution timer."""

from __future__ import annotations

import json
import sys
from typing import Any


def load_event() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(
            f"[no-autoresolution-guard] invalid input JSON: {exc}",
            file=sys.stderr,
        )
        return {}
    if not isinstance(value, dict):
        print(
            "[no-autoresolution-guard] input must be a JSON object",
            file=sys.stderr,
        )
        return {}
    return value


def must_deny(event: dict[str, Any]) -> bool:
    if event.get("hook_event_name") not in {None, "PreToolUse"}:
        return False
    if event.get("tool_name") != "request_user_input":
        return False
    tool_input = event.get("tool_input")
    return isinstance(tool_input, dict) and "autoResolutionMs" in tool_input


def emit_denial() -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        "[user-choice-wait-policy] Remove autoResolutionMs and "
                        "retry the request. User-owned choices wait indefinitely "
                        "for an explicit answer; silence or elapsed time never "
                        "selects an option."
                    ),
                }
            },
            ensure_ascii=False,
        )
    )


def main() -> int:
    if must_deny(load_event()):
        emit_denial()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
