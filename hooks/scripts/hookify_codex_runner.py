#!/usr/bin/env python3
"""Apply controlled global Markdown rules to Codex PreToolUse payloads.

The adapter intentionally loads only ``~/.codex/hookify/*.md``. Repository
hooks must use Codex native project discovery and trust through
``<repo>/.codex/hooks.json`` or ``<repo>/.codex/config.toml``.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any


RULE_DIR = Path.home() / ".codex" / "hookify"
PATCH_FILE_RE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", re.MULTILINE)
SUPPORTED_EVENTS = {"bash", "file"}
SUPPORTED_ACTIONS = {"warn", "block"}
SUPPORTED_OPERATORS = {
    "contains",
    "ends_with",
    "equals",
    "not_contains",
    "regex_match",
    "regex_not_match",
    "starts_with",
}
SUPPORTED_FIELDS = {
    "all",
    "command",
    "content",
    "file_path",
    "new_text",
    "old_text",
    "patch",
    "tool_name",
}
SUPPORTED_META = {"action", "conditions", "enabled", "event", "name", "pattern"}
RULE_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class RuleError(ValueError):
    """Raised when a Markdown rule is malformed."""


@dataclass(frozen=True)
class Condition:
    field: str
    operator: str
    pattern: str
    regex: re.Pattern[str] | None = None


@dataclass(frozen=True)
class Rule:
    name: str
    event: str
    action: str
    body: str
    pattern: re.Pattern[str] | None
    conditions: tuple[Condition, ...]
    path: Path


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
        raise RuleError("missing opening YAML frontmatter delimiter")
    closing = text.find("\n---", 4)
    if closing < 0:
        raise RuleError("missing closing YAML frontmatter delimiter")
    raw_meta = text[4:closing]
    body = text[closing + 4 :].lstrip("\n")
    meta: dict[str, Any] = {}
    current_condition: dict[str, Any] | None = None
    in_conditions = False

    for raw_line in raw_meta.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "conditions:":
            meta["conditions"] = []
            in_conditions = True
            current_condition = None
            continue
        if in_conditions and stripped.startswith("- "):
            current_condition = {}
            meta["conditions"].append(current_condition)
            rest = stripped[2:].strip()
            if rest:
                if ":" not in rest:
                    raise RuleError(f"invalid condition line: {stripped}")
                key, value = rest.split(":", 1)
                current_condition[key.strip()] = parse_scalar(value)
            continue
        if in_conditions and raw_line[:1].isspace() and current_condition is not None:
            if ":" not in stripped:
                raise RuleError(f"invalid condition field: {stripped}")
            key, value = stripped.split(":", 1)
            current_condition[key.strip()] = parse_scalar(value)
            continue
        in_conditions = False
        current_condition = None
        if ":" not in stripped:
            raise RuleError(f"invalid frontmatter line: {stripped}")
        key, value = stripped.split(":", 1)
        meta[key.strip()] = parse_scalar(value)
    return meta, body


def compile_regex(pattern: str) -> re.Pattern[str]:
    return re.compile(pattern, flags=re.MULTILINE)


def compile_rule(path: Path) -> Rule | None:
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    unknown = sorted(set(meta) - SUPPORTED_META)
    if unknown:
        raise RuleError(f"unsupported frontmatter field(s): {', '.join(unknown)}")

    enabled = meta.get("enabled", True)
    if not isinstance(enabled, bool):
        raise RuleError("enabled must be true or false")
    if not enabled:
        return None

    name = meta.get("name")
    if not isinstance(name, str) or not RULE_NAME_RE.fullmatch(name):
        raise RuleError("name must be non-empty kebab-case")
    event = meta.get("event")
    if event not in SUPPORTED_EVENTS:
        raise RuleError("event must be bash or file")
    action = meta.get("action", "warn")
    if action not in SUPPORTED_ACTIONS:
        raise RuleError("action must be warn or block")
    body = body.strip()
    if not body:
        raise RuleError("message body must not be empty")

    raw_pattern = meta.get("pattern")
    raw_conditions = meta.get("conditions")
    if raw_pattern is not None and raw_conditions:
        raise RuleError("use pattern or conditions, not both")
    if raw_pattern is None and not raw_conditions:
        raise RuleError("rule requires pattern or conditions")

    pattern: re.Pattern[str] | None = None
    conditions: list[Condition] = []
    if raw_pattern is not None:
        if not isinstance(raw_pattern, str) or not raw_pattern:
            raise RuleError("pattern must be a non-empty string")
        pattern = compile_regex(raw_pattern)
    else:
        if not isinstance(raw_conditions, list):
            raise RuleError("conditions must be a list")
        for index, raw in enumerate(raw_conditions):
            if not isinstance(raw, dict):
                raise RuleError(f"condition {index + 1} must be a mapping")
            unknown_condition = sorted(set(raw) - {"field", "operator", "pattern"})
            if unknown_condition:
                raise RuleError(
                    f"condition {index + 1} has unsupported field(s): "
                    + ", ".join(unknown_condition)
                )
            field = raw.get("field")
            operator = raw.get("operator", "regex_match")
            condition_pattern = raw.get("pattern")
            if field not in SUPPORTED_FIELDS:
                raise RuleError(f"condition {index + 1} uses unsupported field: {field}")
            if operator not in SUPPORTED_OPERATORS:
                raise RuleError(
                    f"condition {index + 1} uses unsupported operator: {operator}"
                )
            if not isinstance(condition_pattern, str):
                raise RuleError(f"condition {index + 1} pattern must be a string")
            regex = None
            if operator in {"regex_match", "regex_not_match"}:
                regex = compile_regex(condition_pattern)
            conditions.append(
                Condition(
                    field=str(field),
                    operator=str(operator),
                    pattern=condition_pattern,
                    regex=regex,
                )
            )

    return Rule(
        name=name,
        event=event,
        action=action,
        body=body,
        pattern=pattern,
        conditions=tuple(conditions),
        path=path,
    )


def load_rules() -> tuple[list[Rule], list[str]]:
    rules: list[Rule] = []
    diagnostics: list[str] = []
    names: set[str] = set()
    if not RULE_DIR.is_dir():
        return rules, diagnostics

    for path in sorted(RULE_DIR.glob("*.md")):
        if path.name.casefold() == "readme.md":
            continue
        try:
            rule = compile_rule(path)
            if rule is None:
                continue
            if rule.name in names:
                raise RuleError(f"duplicate enabled rule name: {rule.name}")
            names.add(rule.name)
            rules.append(rule)
        except (OSError, RuleError, re.error) as exc:
            diagnostics.append(f"{path}: {exc}")
    return rules, diagnostics


def load_event() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"[codex-hook-rules] invalid input JSON: {exc}", file=sys.stderr)
        return {}
    if not isinstance(value, dict):
        print("[codex-hook-rules] input must be a JSON object", file=sys.stderr)
        return {}
    return value


def event_kind(event: dict[str, Any]) -> str:
    tool_name = event.get("tool_name")
    if tool_name == "Bash":
        return "bash"
    if tool_name == "apply_patch":
        return "file"
    return ""


def command_text(event: dict[str, Any]) -> str | None:
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    value = tool_input.get("command")
    return value if isinstance(value, str) else None


def patch_file_paths(text: str) -> list[str]:
    return [match.strip() for match in PATCH_FILE_RE.findall(text) if match.strip()]


def field_map(event: dict[str, Any], kind: str, text: str) -> dict[str, str]:
    paths = patch_file_paths(text) if kind == "file" else []
    return {
        "all": text,
        "command": text if kind == "bash" else "",
        "content": text,
        "file_path": "\n".join(paths),
        "new_text": text if kind == "file" else "",
        "old_text": "",
        "patch": text if kind == "file" else "",
        "tool_name": str(event.get("tool_name") or ""),
    }


def condition_matches(condition: Condition, value: str) -> bool:
    if condition.operator == "regex_match":
        assert condition.regex is not None
        return condition.regex.search(value) is not None
    if condition.operator == "regex_not_match":
        assert condition.regex is not None
        return condition.regex.search(value) is None
    if condition.operator == "contains":
        return condition.pattern in value
    if condition.operator == "not_contains":
        return condition.pattern not in value
    if condition.operator == "equals":
        return value == condition.pattern
    if condition.operator == "starts_with":
        return value.startswith(condition.pattern)
    if condition.operator == "ends_with":
        return value.endswith(condition.pattern)
    return False


def rule_matches(rule: Rule, kind: str, fields: dict[str, str]) -> bool:
    if rule.event != kind:
        return False
    if rule.pattern is not None:
        target = fields["command"] if kind == "bash" else fields["all"]
        return rule.pattern.search(target) is not None
    return all(
        condition_matches(condition, fields.get(condition.field, ""))
        for condition in rule.conditions
    )


def rule_message(rule: Rule) -> str:
    return f"[codex-hook-rule:{rule.name}]\n{rule.body}"


def emit_invalid_payload(tool_name: str) -> None:
    print(
        json.dumps(
            {
                "systemMessage": (
                    "Codex hook rules skipped an unsupported "
                    f"{tool_name} payload: expected tool_input.command to be a string."
                )
            },
            ensure_ascii=False,
        )
    )


def emit_matches(blocks: list[str], warnings: list[str]) -> None:
    if blocks:
        value = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "\n\n".join(blocks),
            }
        }
    elif warnings:
        value = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": "\n\n".join(warnings),
            }
        }
    else:
        return
    print(json.dumps(value, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    args = parser.parse_args()
    if args.event != "PreToolUse":
        return 0

    event = load_event()
    kind = event_kind(event)
    if not kind:
        return 0
    text = command_text(event)
    if text is None:
        emit_invalid_payload(str(event.get("tool_name") or "unknown"))
        return 0

    rules, diagnostics = load_rules()
    for diagnostic in diagnostics:
        print(f"[codex-hook-rules] {diagnostic}", file=sys.stderr)

    fields = field_map(event, kind, text)
    blocks: list[str] = []
    warnings: list[str] = []
    for rule in rules:
        if not rule_matches(rule, kind, fields):
            continue
        message = rule_message(rule)
        if rule.action == "block":
            blocks.append(message)
        else:
            warnings.append(message)
    emit_matches(blocks, warnings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
