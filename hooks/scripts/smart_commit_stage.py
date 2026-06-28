#!/usr/bin/env python3
"""Track files touched by Codex edits and stage them after explicit acceptance.

Record mode stores edited files in a pending list. Confirm mode stages pending
files only when the user prompt explicitly says the work has been accepted or
asks for staging. It never creates commits and never runs `git add .`.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


PATCH_FILE_RE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", re.MULTILINE)
CONFIRM_RE = re.compile(
    r"(验收通过|确认验收|已验收|验收完成|"
    r"可以\s*(?:暂存|git\s+add|add|stage)|"
    r"请\s*(?:暂存|git\s+add|add|stage)|"
    r"帮我\s*(?:暂存|git\s+add|add|stage)|"
    r"(?:please|can\s+you)\s+(?:git\s+add|add|stage)\b|"
    r"(?:^|[\s,，。；;])git\s+add(?:[\s,，。；;]|$))",
    re.IGNORECASE,
)
NEGATIVE_RE = re.compile(
    r"(不要|别|先不|暂不|不(?:要|用|必|需要)?\s*(?:暂存|add|stage|提交|commit)|"
    r"no\s+(?:stage|add|commit))",
    re.IGNORECASE,
)
PENDING_PATH_ENV = "SMART_COMMIT_PENDING_PATH"


def load_event() -> dict[str, Any]:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=str(cwd), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def git_root(cwd: Path) -> Path | None:
    result = run(["git", "rev-parse", "--show-toplevel"], cwd)
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip())


def event_cwd(event: dict[str, Any]) -> Path:
    tool_input = event.get("tool_input") if isinstance(event.get("tool_input"), dict) else {}
    value = event.get("cwd") or event.get("workdir") or tool_input.get("workdir") or os.getcwd()
    return Path(str(value)).expanduser()


def touched_paths(event: dict[str, Any], cwd: Path) -> list[Path]:
    tool_input = event.get("tool_input") or {}
    paths: list[str] = []
    patch_text = ""
    if isinstance(tool_input, str):
        patch_text = tool_input
    elif isinstance(tool_input, dict):
        for key in ("file_path", "path", "filename"):
            value = tool_input.get(key)
            if isinstance(value, str) and value:
                paths.append(value)
        value = tool_input.get("patch") or tool_input.get("content")
        if isinstance(value, str):
            patch_text = value
    paths.extend(PATCH_FILE_RE.findall(patch_text))

    resolved: list[Path] = []
    seen: set[Path] = set()
    for raw in paths:
        path = Path(raw)
        if not path.is_absolute():
            path = cwd / path
        try:
            path = path.resolve()
        except OSError:
            path = path.absolute()
        if path not in seen:
            seen.add(path)
            resolved.append(path)
    return resolved


def pending_state_path() -> Path:
    value = os.environ.get(PENDING_PATH_ENV)
    if value:
        return Path(value).expanduser()
    return Path.home() / ".codex" / "hooks" / ".smart_commit_pending.json"


def load_state(path: Path) -> dict[str, Any]:
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"repos": {}}
    if not isinstance(state, dict):
        return {"repos": {}}
    repos = state.get("repos")
    if not isinstance(repos, dict):
        state["repos"] = {}
    return state


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(path.name + ".tmp")
    tmp_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def prompt_text(event: dict[str, Any]) -> str:
    tool_input = event.get("tool_input") if isinstance(event.get("tool_input"), dict) else {}
    candidates = [
        event.get("user_prompt"),
        event.get("prompt"),
        event.get("message"),
        event.get("text"),
        tool_input.get("user_prompt"),
        tool_input.get("prompt"),
        tool_input.get("message"),
        tool_input.get("content"),
    ]
    return "\n".join(str(value) for value in candidates if isinstance(value, str))


def is_acceptance_prompt(text: str) -> bool:
    return bool(text and CONFIRM_RE.search(text) and not NEGATIVE_RE.search(text))


def record_pending(event: dict[str, Any]) -> int:
    cwd = event_cwd(event)
    root = git_root(cwd)
    if root is None:
        return 0

    paths = []
    for path in touched_paths(event, cwd):
        try:
            path.relative_to(root)
        except ValueError:
            continue
        paths.append(path)
    if not paths:
        return 0

    rel_paths = [str(path.relative_to(root)) for path in paths]
    state_path = pending_state_path()
    state = load_state(state_path)
    repos = state.setdefault("repos", {})
    repo_state = repos.setdefault(str(root), {"paths": []})
    existing = list(repo_state.get("paths") or [])
    seen = set(existing)
    for rel_path in rel_paths:
        if rel_path not in seen:
            existing.append(rel_path)
            seen.add(rel_path)
    repo_state["paths"] = existing
    write_state(state_path, state)

    print(
        "[smart-commit] Pending review before staging: "
        + ", ".join(rel_paths)
        + ". Say '验收通过' or '可以暂存' to stage pending files."
    )
    return 0


def candidate_roots(event: dict[str, Any], state: dict[str, Any]) -> list[Path]:
    repos = state.get("repos")
    if not isinstance(repos, dict) or not repos:
        return []

    cwd_root = git_root(event_cwd(event))
    if cwd_root is not None and str(cwd_root) in repos:
        return [cwd_root]
    if len(repos) == 1:
        return [Path(next(iter(repos)))]
    return []


def stage_pending(event: dict[str, Any]) -> int:
    if not is_acceptance_prompt(prompt_text(event)):
        return 0

    state_path = pending_state_path()
    state = load_state(state_path)
    repos = state.get("repos")
    if not isinstance(repos, dict) or not repos:
        print("[smart-commit] No pending files to stage.")
        return 0

    roots = candidate_roots(event, state)
    if not roots:
        print("[smart-commit] Pending files span multiple repositories; stage from the target repo.")
        return 0

    staged: list[str] = []
    for root in roots:
        repo_state = repos.get(str(root))
        if not isinstance(repo_state, dict):
            continue
        rel_paths = [str(path) for path in repo_state.get("paths") or [] if isinstance(path, str)]
        if not rel_paths:
            repos.pop(str(root), None)
            continue

        status = run(["git", "status", "--short", "--", *rel_paths], root)
        if status.returncode != 0:
            print(f"[smart-commit] git status failed in {root}: {status.stderr.strip()}")
            continue
        change_lines = [line.strip() for line in status.stdout.splitlines() if line.strip()]
        if not change_lines:
            print(f"[smart-commit] No current changes for pending file(s) in {root}.")
            repos.pop(str(root), None)
            continue
        preview = ", ".join(change_lines[:8])
        if len(change_lines) > 8:
            preview += f", ... (+{len(change_lines) - 8} more)"
        print(f"[smart-commit] About to stage current changes: {preview}")

        result = run(["git", "add", "-A", "--", *rel_paths], root)
        if result.returncode != 0:
            print(f"[smart-commit] git add failed in {root}: {result.stderr.strip()}")
            continue

        staged.extend(f"{root}:{path}" for path in rel_paths)
        repos.pop(str(root), None)

    write_state(state_path, state)
    if staged:
        print("[smart-commit] Staged accepted file(s): " + ", ".join(staged))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("record", "confirm"), default="record")
    args = parser.parse_args()

    event = load_event()
    if args.mode == "confirm":
        return stage_pending(event)
    return record_pending(event)


if __name__ == "__main__":
    raise SystemExit(main())
