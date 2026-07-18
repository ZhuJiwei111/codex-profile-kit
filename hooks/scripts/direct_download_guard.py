#!/usr/bin/env python3
"""Give stateless, non-blocking route advice for likely large transfers."""

from __future__ import annotations

import json
import re
import shlex
import sys
from typing import Any


CONTROL_TOKEN_RE = re.compile(r"^[;&|()]+$")
ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=(.*)$", re.DOTALL)
LARGE_MARKER_RE = re.compile(
    r"(?:"
    r"\.(?:tar\.gz|tgz|tar|zip|7z|rar|zst|gz|bz2|xz|h5|h5ad|loom|"
    r"mtx|tsv\.gz|csv\.gz|bed\.gz|fastq\.gz|fq\.gz|safetensors|"
    r"pt|pth|ckpt|bin|onnx|parquet|arrow)(?:$|[?#])"
    r"|(?:^|[/\\])(?:data|datasets|checkpoints|models|weights|raw|artifacts)(?:[/\\]|$)"
    r")",
    re.IGNORECASE,
)


def load_event() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"[direct-download-guard] invalid input JSON: {exc}", file=sys.stderr)
        return {}
    return value if isinstance(value, dict) else {}


def command_text(event: dict[str, Any]) -> str | None:
    if event.get("tool_name") != "Bash":
        return None
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    value = tool_input.get("command")
    return value if isinstance(value, str) else None


def shell_segments(command: str) -> list[list[str]]:
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()")
        lexer.whitespace_split = True
        lexer.commenters = ""
        tokens = list(lexer)
    except ValueError:
        return []

    segments: list[list[str]] = []
    current: list[str] = []
    for token in tokens:
        if CONTROL_TOKEN_RE.fullmatch(token):
            if current:
                segments.append(current)
                current = []
            continue
        current.append(token)
    if current:
        segments.append(current)
    return segments


def assignment(tokens: list[str], index: int) -> tuple[str, str] | None:
    if index >= len(tokens):
        return None
    token = tokens[index]
    match = ASSIGNMENT_RE.fullmatch(token)
    if not match:
        return None
    return token.split("=", 1)[0], match.group(1)


def unwrap_segment(tokens: list[str]) -> tuple[list[str], set[str]]:
    """Return command tokens and proxy variables explicitly unset for them."""

    index = 0
    unset_vars: set[str] = set()

    while assignment(tokens, index) is not None:
        index += 1

    if index < len(tokens) and tokens[index] == "env":
        index += 1
        while index < len(tokens):
            token = tokens[index]
            if token == "--":
                index += 1
                break
            if token in {"-u", "--unset"} and index + 1 < len(tokens):
                unset_vars.add(tokens[index + 1])
                index += 2
                continue
            if token.startswith("--unset="):
                unset_vars.add(token.split("=", 1)[1])
                index += 1
                continue
            item = assignment(tokens, index)
            if item is not None:
                index += 1
                continue
            if token.startswith("-"):
                index += 1
                continue
            break

    if index < len(tokens) and tokens[index] == "proxy_off":
        index += 1

    return tokens[index:], unset_vars


def curl_download(tokens: list[str]) -> bool:
    for token in tokens[1:]:
        if token in {"-o", "-O", "--output", "--output-dir", "--remote-name"}:
            return True
        if token.startswith(("--output=", "--output-dir=")):
            return True
        if re.fullmatch(r"-[A-Za-z]*[oO][A-Za-z]*", token):
            return True
    return False


def transfer_kind(tokens: list[str]) -> str | None:
    if not tokens:
        return None
    command = tokens[0].rsplit("/", 1)[-1].casefold()
    args = [token.casefold() for token in tokens[1:]]
    if command == "wget" and "--spider" in args:
        return None
    if command in {"wget", "aria2c", "axel"}:
        return command
    if command == "curl" and curl_download(tokens):
        return command
    if command in {"hf", "huggingface-cli"} and args[:1] == ["download"]:
        return "huggingface"
    if command == "aws" and len(args) >= 2 and args[0] == "s3" and args[1] in {"cp", "sync"}:
        return "aws"
    if command == "gsutil" and args[:1] and args[0] in {"cp", "rsync"}:
        return "gsutil"
    if command == "rclone" and args[:1] and args[0] in {"copy", "copyto", "move", "sync"}:
        return "rclone"
    return None


def is_large_transfer(tokens: list[str], kind: str) -> bool:
    if kind == "huggingface":
        return True
    return LARGE_MARKER_RE.search("\n".join(tokens)) is not None


def large_transfer_segments(command: str) -> list[list[str]]:
    transfers: list[list[str]] = []
    for segment in shell_segments(command):
        command_tokens, _ = unwrap_segment(segment)
        kind = transfer_kind(command_tokens)
        if kind is None or not is_large_transfer(command_tokens, kind):
            continue
        transfers.append(command_tokens)
    return transfers


def emit_warning() -> None:
    context = (
        "A likely large transfer is planned. When reasonable, make a small direct "
        "probe to the same destination first. If direct access then fails with a "
        "deterministic connection error, consult the current host's HOST_LOCAL "
        "connection helper. Reuse explicit authority for that exact proxy retry; "
        "otherwise request user authorization before retrying the identical "
        "transfer through a proxy. This advice is stateless and "
        "non-blocking; Codex and the user decide how to proceed."
    )
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": context,
                }
            }
        )
    )


def main() -> int:
    event = load_event()
    command = command_text(event)
    if not command:
        return 0
    if large_transfer_segments(command):
        emit_warning()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
