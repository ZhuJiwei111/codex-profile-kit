#!/usr/bin/env python3
"""Deny direct Conda install/create commands that target base."""

from __future__ import annotations

import json
import ntpath
import os
from pathlib import Path
import re
import shlex
import sys
from typing import Any


ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
BOUNDARY_CHARS = frozenset(";&|()\n")
CONDA_EXECUTABLES = {
    name + suffix
    for name in ("conda", "mamba")
    for suffix in ("", ".exe", ".bat", ".cmd")
}


def load_event() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"[conda-base-guard] invalid input JSON: {exc}", file=sys.stderr)
        return {}
    return value if isinstance(value, dict) else {}


def strip_comments(command: str) -> str:
    output: list[str] = []
    quote: str | None = None
    escaped = False
    in_comment = False
    word_start = True

    for character in command:
        if in_comment:
            if character == "\n":
                output.append(character)
                in_comment = False
                word_start = True
            continue
        if escaped:
            output.append(character)
            escaped = False
            word_start = False
            continue
        if quote == "'":
            output.append(character)
            if character == "'":
                quote = None
            continue
        if quote == '"':
            output.append(character)
            if character == "\\":
                escaped = True
            elif character == '"':
                quote = None
            continue
        if character == "\\":
            output.append(character)
            escaped = True
            word_start = False
        elif character in {"'", '"'}:
            output.append(character)
            quote = character
            word_start = False
        elif character == "#" and word_start:
            in_comment = True
        else:
            output.append(character)
            word_start = character.isspace() or character in BOUNDARY_CHARS
    return "".join(output)


def command_segments(command: str) -> list[list[str]]:
    lexer = shlex.shlex(
        strip_comments(command),
        posix=True,
        punctuation_chars=";&|()\n",
    )
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    lexer.commenters = ""
    if os.name == "nt":
        # PowerShell and cmd paths use backslashes as separators, not escapes.
        lexer.escape = ""
    try:
        tokens = list(lexer)
    except ValueError:
        return []

    segments: list[list[str]] = []
    current: list[str] = []
    for token in tokens:
        if token and set(token) <= BOUNDARY_CHARS:
            if current:
                segments.append(current)
                current = []
        else:
            current.append(token)
    if current:
        segments.append(current)
    return segments


def direct_invocation(segment: list[str]) -> list[str]:
    index = 0
    while index < len(segment) and ASSIGNMENT.match(segment[index]):
        index += 1
    return segment[index:]


def mutation_arguments(argv: list[str]) -> list[str] | None:
    if len(argv) >= 3 and [part.casefold() for part in argv[1:3]] == [
        "env",
        "create",
    ]:
        return argv[3:]
    if len(argv) >= 2 and argv[1].casefold() in {"create", "install"}:
        return argv[2:]
    return None


def option_values(arguments: list[str], short: str, long: str) -> list[str]:
    values: list[str] = []
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        folded = argument.casefold()
        if argument == "--":
            break
        if folded in {short, long}:
            if index + 1 < len(arguments):
                values.append(arguments[index + 1])
                index += 2
                continue
        elif folded.startswith(f"{long}=") or folded.startswith(f"{short}="):
            values.append(argument.split("=", 1)[1])
        elif folded.startswith(short) and len(argument) > len(short):
            values.append(argument[len(short) :])
        index += 1
    return values


def normalized_path(value: str) -> str:
    return os.path.normcase(
        os.path.normpath(os.path.expandvars(os.path.expanduser(value)))
    )


def conda_roots() -> set[str]:
    explicit = os.environ.get("CONDA_ROOT")
    roots = {normalized_path(explicit)} if explicit else set()
    runtime = Path(sys.prefix)
    if runtime.parent.name.casefold() == "envs":
        runtime = runtime.parent.parent
    candidates = [runtime]
    executable = os.environ.get("CONDA_EXE")
    if executable:
        parent = Path(executable).parent
        if parent.name.casefold() in {"scripts", "bin", "condabin"}:
            root = parent.parent
            if root.name.casefold() == "library":
                root = root.parent
            candidates.append(root)
    for candidate in candidates:
        if (candidate / "conda-meta").is_dir() and (candidate / "condabin").is_dir():
            roots.add(normalized_path(str(candidate)))
    return roots


def targets_base(command: str) -> bool:
    roots = conda_roots()

    for segment in command_segments(command):
        argv = direct_invocation(segment)
        if (
            not argv
            or ntpath.basename(argv[0]).casefold() not in CONDA_EXECUTABLES
        ):
            continue
        arguments = mutation_arguments(argv)
        if arguments is None:
            continue
        if any(
            value.casefold() == "base"
            for value in option_values(arguments, "-n", "--name")
        ):
            return True
        if roots and any(
            normalized_path(value) in roots
            for value in option_values(arguments, "-p", "--prefix")
        ):
            return True
    return False


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
