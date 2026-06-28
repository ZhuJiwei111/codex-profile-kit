#!/usr/bin/env python3
"""Run Hookify-style markdown rules as Codex native hooks.

Rule locations:
- Global: ~/.codex/hookify/*.md
- Project: .codex/hookify*.md and .codex/hookify/*.md

Supported frontmatter fields:
- name, enabled, event, action, pattern
- conditions: list of {field, operator, pattern}
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
from typing import Any


FILE_TOOLS = {"Edit", "Write", "MultiEdit", "apply_patch", "functions.apply_patch"}
BASH_TOOLS = {"Bash", "bash", "exec_command", "functions.exec_command"}
PATCH_FILE_RE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", re.MULTILINE)


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    raw_meta = parts[1].strip("\n")
    body = parts[2].lstrip("\n")
    meta: dict[str, Any] = {}
    current_condition: dict[str, Any] | None = None
    in_conditions = False

    for raw_line in raw_meta.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "conditions:":
            meta["conditions"] = []
            in_conditions = True
            current_condition = None
            continue
        if in_conditions and stripped.startswith("- "):
            current_condition = {}
            meta.setdefault("conditions", []).append(current_condition)
            rest = stripped[2:].strip()
            if ":" in rest:
                key, value = rest.split(":", 1)
                current_condition[key.strip()] = parse_scalar(value)
            continue
        if in_conditions and raw_line.startswith(" ") and current_condition is not None:
            if ":" in stripped:
                key, value = stripped.split(":", 1)
                current_condition[key.strip()] = parse_scalar(value)
            continue
        in_conditions = False
        current_condition = None
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            meta[key.strip()] = parse_scalar(value)
    return meta, body


def rule_files(cwd: Path) -> list[Path]:
    candidates: list[Path] = []
    locations = [
        Path.home() / ".codex" / "hookify",
        cwd / ".codex",
        cwd / ".codex" / "hookify",
    ]
    for location in locations:
        if not location.is_dir():
            continue
        candidates.extend(sorted(location.glob("hookify*.md")))
        candidates.extend(sorted(location.glob("*.local.md")))
        candidates.extend(sorted(location.glob("*.md")))
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in candidates:
        resolved = path.resolve()
        if resolved not in seen and path.is_file():
            seen.add(resolved)
            unique.append(path)
    return unique


def load_event() -> dict[str, Any]:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def tool_name(event: dict[str, Any]) -> str:
    value = event.get("tool_name") or event.get("tool") or event.get("name")
    if isinstance(value, str):
        return value
    tool_input = event.get("tool_input")
    if isinstance(tool_input, dict):
        value = tool_input.get("tool_name") or tool_input.get("name")
        if isinstance(value, str):
            return value
    return ""


def tool_input_text(event: dict[str, Any]) -> tuple[dict[str, Any], str]:
    tool_input = event.get("tool_input") or {}
    if isinstance(tool_input, str):
        return {"content": tool_input, "patch": tool_input}, tool_input
    if isinstance(tool_input, dict):
        return tool_input, json.dumps(tool_input, ensure_ascii=False)
    return {}, ""


def patch_file_paths(text: str) -> list[str]:
    return [match.strip() for match in PATCH_FILE_RE.findall(text) if match.strip()]


def field_map(event: dict[str, Any]) -> dict[str, str]:
    tool_input, serialized = tool_input_text(event)
    file_path_values: list[str] = []
    if isinstance(tool_input, dict):
        for key in ("file_path", "path", "filename"):
            value = tool_input.get(key)
            if isinstance(value, str) and value:
                file_path_values.append(value)
        patch_text = tool_input.get("patch") or tool_input.get("content") or ""
        if isinstance(patch_text, str):
            file_path_values.extend(patch_file_paths(patch_text))
    prompt = (
        event.get("user_prompt")
        or event.get("prompt")
        or event.get("message")
        or tool_input.get("user_prompt")
        or ""
    )
    command = tool_input.get("command") or tool_input.get("cmd") or ""
    content = (
        tool_input.get("content")
        or tool_input.get("patch")
        or tool_input.get("new_text")
        or tool_input.get("text")
        or serialized
    )
    return {
        "command": str(command),
        "file_path": "\n".join(file_path_values),
        "new_text": str(tool_input.get("new_text") or tool_input.get("content") or ""),
        "old_text": str(tool_input.get("old_text") or ""),
        "content": str(content),
        "patch": str(tool_input.get("patch") or content),
        "user_prompt": str(prompt),
        "tool_name": tool_name(event),
        "all": "\n".join(str(v) for v in tool_input.values())
        if isinstance(tool_input, dict)
        else serialized,
    }


def applies_to_event(rule_event: str, codex_event: str, event: dict[str, Any]) -> bool:
    wanted = rule_event.lower()
    if wanted == "all":
        return True
    actual = codex_event.lower()
    name = tool_name(event)
    fields = field_map(event)
    if wanted == "bash":
        return actual in {"pretooluse", "posttooluse"} and (
            name in BASH_TOOLS or bool(fields["command"])
        )
    if wanted == "file":
        return actual in {"pretooluse", "posttooluse"} and (
            name in FILE_TOOLS or bool(fields["file_path"]) or bool(fields["patch"])
        )
    if wanted == "prompt":
        return actual == "userpromptsubmit"
    if wanted == "stop":
        return actual == "stop"
    return wanted == actual


def operator_matches(value: str, operator: str, pattern: str) -> bool:
    if operator == "regex_match":
        return re.search(pattern, value, flags=re.MULTILINE) is not None
    if operator == "contains":
        return pattern in value
    if operator == "equals":
        return value == pattern
    if operator == "not_contains":
        return pattern not in value
    if operator == "starts_with":
        return value.startswith(pattern)
    if operator == "ends_with":
        return value.endswith(pattern)
    return False


def rule_matches(meta: dict[str, Any], codex_event: str, event: dict[str, Any]) -> bool:
    if meta.get("enabled", True) is False:
        return False
    if not applies_to_event(str(meta.get("event", "all")), codex_event, event):
        return False
    fields = field_map(event)
    conditions = meta.get("conditions")
    if isinstance(conditions, list) and conditions:
        for condition in conditions:
            if not isinstance(condition, dict):
                return False
            field = str(condition.get("field", "all"))
            operator = str(condition.get("operator", "regex_match"))
            pattern = str(condition.get("pattern", ""))
            if not operator_matches(fields.get(field, ""), operator, pattern):
                return False
        return True
    pattern = meta.get("pattern")
    if pattern is None:
        return False
    rule_event = str(meta.get("event", "all")).lower()
    target_field = {
        "bash": "command",
        "file": "all",
        "prompt": "user_prompt",
        "stop": "all",
    }.get(rule_event, "all")
    return re.search(str(pattern), fields.get(target_field, ""), flags=re.MULTILINE) is not None


def emit_block(codex_event: str, message: str) -> None:
    if codex_event == "PreToolUse":
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": message,
                    }
                },
                ensure_ascii=False,
            )
        )
    else:
        print(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    args = parser.parse_args()

    event = load_event()
    cwd_text = event.get("cwd") or event.get("workdir") or os.getcwd()
    cwd = Path(str(cwd_text)).expanduser()
    matched: list[tuple[dict[str, Any], str, Path]] = []

    for path in rule_files(cwd):
        try:
            meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        except OSError:
            continue
        try:
            if rule_matches(meta, args.event, event):
                matched.append((meta, body.strip(), path))
        except re.error as exc:
            print(f"[hookify-codex] Invalid regex in {path}: {exc}")

    if not matched:
        return 0

    blocks = []
    warnings = []
    for meta, body, path in matched:
        label = meta.get("name") or path.name
        message = f"[hookify-codex:{label}]\n{body}".strip()
        if str(meta.get("action", "warn")).lower() == "block":
            blocks.append(message)
        else:
            warnings.append(message)

    if blocks:
        emit_block(args.event, "\n\n".join(blocks))
    elif warnings:
        print("\n\n".join(warnings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
