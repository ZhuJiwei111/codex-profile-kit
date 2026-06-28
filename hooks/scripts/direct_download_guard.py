#!/usr/bin/env python3
"""Codex PreToolUse guard for large dataset downloads.

Policy:
- Large downloads must explicitly run without proxy environment variables.
- If a command looks like a large download and still relies on the inherited
  proxy environment, block it and ask the agent/user to retry direct.
- Do not fall back to proxy automatically when direct access fails.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys


PROXY_VARS = (
    "HTTPS_PROXY",
    "HTTP_PROXY",
    "ALL_PROXY",
    "https_proxy",
    "http_proxy",
    "all_proxy",
)

NO_PROXY_VARS = ("NO_PROXY", "no_proxy")

DOWNLOAD_TOOLS_RE = re.compile(
    r"\b(aria2c|wget|axel|rclone|aws|gsutil|huggingface-cli|hf)\b",
    re.IGNORECASE,
)

COMMAND_DOWNLOAD_RE = re.compile(
    r"\bcurl\b(?=[^;&|]*\s(?:-O\b|--remote-name\b|-o\b|--output\b|--output-dir\b))",
    re.IGNORECASE,
)

SCRIPT_DOWNLOAD_RE = re.compile(
    r"(^|[\s;&|()])("
    r"(?:bash|zsh|sh)\s+[^;&|]*\bdown(?:load)?\.sh\b"
    r"|RUN_DOWNLOAD=1\b"
    r"|conda\s+env\s+create\b"
    r"|mamba\s+(?:install|create)\b"
    r"|pip\s+install\s+-r\b"
    r"|uv\s+sync\b"
    r"|npm\s+install\b"
    r"|pnpm\s+install\b"
    r")",
    re.IGNORECASE,
)

LARGE_FILE_RE = re.compile(
    r"\.(?:"
    r"tar\.gz|tgz|tar|zip|7z|rar|zst|gz|bz2|xz|"
    r"h5|h5ad|loom|mtx|tsv\.gz|csv\.gz|bed\.gz|fastq\.gz|fq\.gz|"
    r"safetensors|pt|pth|ckpt|bin|onnx|parquet|arrow"
    r")\b",
    re.IGNORECASE,
)

LARGE_DATA_PATH_RE = re.compile(
    r"\b(data|datasets|checkpoints|models|weights|raw|paired)/",
    re.IGNORECASE,
)

PROXY_OFF_RE = re.compile(r"(^|[;&|()])\s*proxy_off(\s|[;&|)]|$)")
ENV_COMMAND_RE = re.compile(r"(^|[;&|()])\s*env\b([^;&|]*)")
UNSET_COMMAND_RE = re.compile(r"(^|[;&|()])\s*unset\s+([^;&|]*)")


def shell_words(text: str) -> list[str]:
    try:
        return shlex.split(text)
    except ValueError:
        return text.split()


def first_download_index(command: str) -> int:
    starts = []
    for pattern in (DOWNLOAD_TOOLS_RE, COMMAND_DOWNLOAD_RE, SCRIPT_DOWNLOAD_RE):
        match = pattern.search(command)
        if match:
            starts.append(match.start())
    return min(starts) if starts else len(command)


def explicitly_unset_proxy_vars(command: str, before_index: int) -> set[str]:
    unset_vars: set[str] = set()

    for match in ENV_COMMAND_RE.finditer(command):
        if match.start() > before_index:
            continue
        words = shell_words(match.group(2))
        index = 0
        while index < len(words):
            word = words[index]
            if word == "-u" and index + 1 < len(words):
                unset_vars.add(words[index + 1])
                index += 2
                continue
            if word == "--unset" and index + 1 < len(words):
                unset_vars.add(words[index + 1])
                index += 2
                continue
            if word.startswith("--unset="):
                unset_vars.add(word.split("=", 1)[1])
            index += 1

    for match in UNSET_COMMAND_RE.finditer(command):
        if match.start() > before_index:
            continue
        for word in shell_words(match.group(2)):
            if not word.startswith("-"):
                unset_vars.add(word)

    return unset_vars


def explicitly_direct(command: str, before_index: int) -> bool:
    proxy_off_match = PROXY_OFF_RE.search(command)
    if proxy_off_match and proxy_off_match.start() <= before_index:
        return True
    unset_vars = explicitly_unset_proxy_vars(command, before_index)
    return all(name in unset_vars for name in PROXY_VARS)


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    tool_input = event.get("tool_input") or {}
    command = tool_input.get("command")
    if not isinstance(command, str) or not command.strip():
        return 0

    has_proxy = any(os.environ.get(name) for name in PROXY_VARS)
    if not has_proxy:
        return 0

    looks_like_download = bool(
        DOWNLOAD_TOOLS_RE.search(command)
        or COMMAND_DOWNLOAD_RE.search(command)
        or SCRIPT_DOWNLOAD_RE.search(command)
    )
    looks_large = bool(
        LARGE_FILE_RE.search(command)
        or LARGE_DATA_PATH_RE.search(command)
        or SCRIPT_DOWNLOAD_RE.search(command)
    )
    if looks_like_download and looks_large and not explicitly_direct(command, first_download_index(command)):
        unset_flags = " ".join(f"-u {name}" for name in (*PROXY_VARS, *NO_PROXY_VARS))
        reason = (
            "Large dataset/model download blocked because proxy environment "
            "variables are currently set. Retry with direct networking first "
            "and explicitly unset all proxy variables, "
            "for example:\n\n"
            f"  env {unset_flags} {command}\n\n"
            "If direct access fails, report the failure to the user instead of "
            "falling back to proxy automatically."
        )
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": reason,
                    }
                }
            )
        )
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
