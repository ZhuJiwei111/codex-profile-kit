#!/usr/bin/env python3
"""Block three narrow, deterministic local safety violations."""

from __future__ import annotations

import json
import re
import sys
from typing import Any


PATCH_FILE_RE = re.compile(
    r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", re.MULTILINE
)
SENSITIVE_PATH_RE = re.compile(
    r"(^|/)(?:\.netrc|id_(?:rsa|dsa|ecdsa|ed25519)(?:\.[^/\n]+)?|"
    r"[^/\n]*private[^/\n]*\.pem|[^/\n]+\.(?:key|p12|pfx)|"
    r"\.secrets(?:/.*)?|\.codex/(?:auth(?:\.json)?|credentials|tokens?|"
    r"sessions?|archived_sessions|history\.jsonl|session_index\.jsonl)"
    r"(?:/.*)?)$",
    re.IGNORECASE | re.MULTILINE,
)
CONDA_BASE_RE = re.compile(
    r"(^|[\s;&|()])(?:(?:conda|mamba)\s+(?:env\s+create|install|create)\b"
    r"[^\n;&|]*(?:(?:-n|--name)(?:\s+|=)base\b|(?:-p|--prefix)"
    r"(?:\s+|=)[^ \n;&|]*/(?:(?:mini)?conda[0-9A-Za-z_.-]*|anaconda3)\b"
    r"(?=$|[\"'\s;&|)]))|conda\s+run\b[^\n;&|]*(?:-n|--name)"
    r"(?:\s+|=)base\b[^\n;&|]*(?:pip3?|python3?\s+-m\s+pip|conda|mamba)"
    r"\s+install\b|conda\s+activate\s+base\b[^\n;&|]*(?:&&|;)\s*"
    r"(?:pip3?|python3?\s+-m\s+pip|conda|mamba)\s+install\b)",
    re.IGNORECASE,
)
SENSITIVE_MUTATION_RE = re.compile(
    r"(?:\b(?:rm|mv|cp|install|touch|truncate|tee|chmod|chown|ln|unlink|"
    r"shred|dd)\b[^\n;&|]*(?:\.netrc|id_(?:rsa|dsa|ecdsa|ed25519)|"
    r"[^ \n;&|]*private[^ \n;&|]*\.pem|[^ \n;&|]+\.(?:key|p12|pfx)|"
    r"\.secrets(?:/|\b)|\.codex/(?:auth(?:\.json)?|credentials|tokens?|"
    r"sessions?|archived_sessions|history\.jsonl|session_index\.jsonl))|"
    r"\b(?:sed|perl)\b[^\n;&|]*(?:-i|-pi)[^\n;&|]*(?:\.netrc|"
    r"id_(?:rsa|dsa|ecdsa|ed25519)|[^ \n;&|]*private[^ \n;&|]*\.pem|"
    r"[^ \n;&|]+\.(?:key|p12|pfx)|\.secrets(?:/|\b)|\.codex/"
    r"(?:auth(?:\.json)?|credentials|tokens?|sessions?|archived_sessions|"
    r"history\.jsonl|session_index\.jsonl))|(?:^|[;&|])[^;\n&|]*"
    r"(?:>>?|2>)\s*[^ \n;&|]*(?:\.netrc|id_(?:rsa|dsa|ecdsa|ed25519)|"
    r"private[^ \n;&|]*\.pem|\.(?:key|p12|pfx)|\.secrets(?:/|\b)|"
    r"\.codex/(?:auth(?:\.json)?|credentials|tokens?|sessions?|"
    r"archived_sessions|history\.jsonl|session_index\.jsonl)))",
    re.IGNORECASE | re.DOTALL,
)


def load_event() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"[local-safety-guard] invalid input JSON: {exc}", file=sys.stderr)
        return {}
    if not isinstance(value, dict):
        print("[local-safety-guard] input must be a JSON object", file=sys.stderr)
        return {}
    return value


def command_text(event: dict[str, Any]) -> str | None:
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    value = tool_input.get("command")
    return value if isinstance(value, str) else None


def patch_paths(patch: str) -> list[str]:
    return [match.strip() for match in PATCH_FILE_RE.findall(patch) if match.strip()]


def violations(event: dict[str, Any]) -> list[tuple[str, str]]:
    if event.get("hook_event_name") not in {None, "PreToolUse"}:
        return []
    tool_name = event.get("tool_name")
    command = command_text(event)
    if command is None:
        return []
    found: list[tuple[str, str]] = []
    if tool_name == "Bash":
        if CONDA_BASE_RE.search(command):
            found.append(
                (
                    "conda-base-install",
                    "An install or environment mutation explicitly targets Conda base. "
                    "Use the project environment or the documented Codex fallback.",
                )
            )
        if SENSITIVE_MUTATION_RE.search(command):
            found.append(
                (
                    "sensitive-path-mutation",
                    "A shell mutation targets credential, session, or private-key "
                    "material. Use a dedicated user-controlled workflow.",
                )
            )
    elif tool_name == "apply_patch":
        if any(SENSITIVE_PATH_RE.search(path) for path in patch_paths(command)):
            found.append(
                (
                    "sensitive-file-edit",
                    "apply_patch targets credential, session, or private-key material. "
                    "Use a dedicated user-controlled workflow.",
                )
            )
    return found


def emit_denial(found: list[tuple[str, str]]) -> None:
    reason = "\n\n".join(f"[local-safety:{label}] {message}" for label, message in found)
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            },
            ensure_ascii=False,
        )
    )


def main() -> int:
    found = violations(load_event())
    if found:
        emit_denial(found)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
