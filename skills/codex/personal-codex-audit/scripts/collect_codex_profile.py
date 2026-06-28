#!/usr/bin/env python3
"""Collect a read-only JSON inventory of reusable Codex profile files."""

from __future__ import annotations

import argparse
import ast
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MAX_TEXT_BYTES = 64 * 1024
MAX_DOC_BYTES = 8 * 1024

EXCLUDED_DIR_PARTS = {
    ".git",
    "attachments",
    "cache",
    "plugins/cache",
    "sessions",
    "archived_sessions",
    "memories",
    "__pycache__",
}

SENSITIVE_NAMES = {
    "auth.json",
    "history.jsonl",
    "session_index.jsonl",
    ".netrc",
}


def read_limited(path: Path, max_bytes: int = MAX_TEXT_BYTES) -> str:
    with path.open("rb") as handle:
        data = handle.read(max_bytes)
    return data.decode("utf-8", errors="replace")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    raw = text[4:end].strip()
    data: dict[str, str] = {}
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        value = value.strip().strip('"').strip("'")
        data[key.strip()] = value
    return data


def first_heading(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or None
    return None


def module_doc_summary(text: str) -> str | None:
    try:
        module = ast.parse(text)
    except SyntaxError:
        return None
    doc = ast.get_docstring(module)
    if not doc:
        return None
    first_line = " ".join(doc.strip().splitlines()).strip()
    if len(first_line) > 240:
        first_line = first_line[:237].rstrip() + "..."
    return first_line or None


def is_sensitive_path(path: Path) -> bool:
    if path.name in SENSITIVE_NAMES:
        return True
    if path.suffix.startswith(".sqlite"):
        return True
    normalized = "/".join(path.parts)
    return any(part in normalized for part in EXCLUDED_DIR_PARTS)


def rel(path: Path, home: Path) -> str:
    try:
        return str(path.relative_to(home))
    except ValueError:
        return str(path)


def collect_agents(home: Path) -> dict[str, Any]:
    agents_path = home / ".codex" / "AGENTS.md"
    result: dict[str, Any] = {
        "path": rel(agents_path, home),
        "exists": agents_path.is_file() and not agents_path.is_symlink(),
        "headings": [],
    }
    if not result["exists"]:
        return result
    text = read_limited(agents_path)
    headings = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            title = stripped[level:].strip()
            headings.append({"level": level, "title": title})
    result["headings"] = headings
    return result


def collect_skills(home: Path) -> list[dict[str, Any]]:
    roots = [
        ("codex", home / ".codex" / "skills"),
        ("agents", home / ".agents" / "skills"),
    ]
    skills: list[dict[str, Any]] = []
    for source, root in roots:
        if not root.is_dir():
            continue
        for skill_dir in sorted(root.iterdir()):
            if not skill_dir.is_dir() or skill_dir.name.startswith(".") or skill_dir.is_symlink():
                continue
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.is_file() or skill_file.is_symlink():
                continue
            text = read_limited(skill_file)
            fm = parse_frontmatter(text)
            skills.append(
                {
                    "source": source,
                    "path": rel(skill_file, home),
                    "folder": skill_dir.name,
                    "name": fm.get("name", ""),
                    "description": fm.get("description", ""),
                }
            )
    return skills


def collect_hookify(home: Path) -> list[dict[str, Any]]:
    root = home / ".codex" / "hookify"
    rules: list[dict[str, Any]] = []
    if not root.is_dir():
        return rules
    for path in sorted(root.glob("*.md")):
        if path.is_symlink() or path.name == "README.md":
            continue
        text = read_limited(path)
        fm = parse_frontmatter(text)
        rules.append(
            {
                "path": rel(path, home),
                "name": fm.get("name", path.stem),
                "enabled": fm.get("enabled", ""),
                "event": fm.get("event", ""),
                "action": fm.get("action", ""),
                "frontmatter_keys": sorted(fm),
                "pattern_present": "pattern" in fm,
                "pattern_length": len(fm.get("pattern", "")),
                "heading": first_heading(text),
            }
        )
    return rules


def collect_native_hooks(home: Path) -> list[dict[str, Any]]:
    root = home / ".codex" / "hooks"
    hooks: list[dict[str, Any]] = []
    if not root.is_dir():
        return hooks
    for path in sorted(root.iterdir()):
        if not path.is_file() or path.is_symlink() or is_sensitive_path(path):
            continue
        item: dict[str, Any] = {
            "path": rel(path, home),
            "name": path.name,
            "suffix": path.suffix,
            "description": "",
        }
        if path.suffix == ".md":
            text = read_limited(path)
            fm = parse_frontmatter(text)
            item["description"] = fm.get("description", "") or first_heading(text) or ""
        elif path.suffix == ".py":
            text = read_limited(path, MAX_DOC_BYTES)
            item["description"] = module_doc_summary(text) or ""
        hooks.append(item)
    return hooks


def collect_profile(home: Path) -> dict[str, Any]:
    home = home.expanduser().resolve()
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "home": str(home),
        "read_only": True,
        "agents": collect_agents(home),
        "skills": collect_skills(home),
        "hookify_rules": collect_hookify(home),
        "native_hooks": collect_native_hooks(home),
        "excluded_by_default": sorted(SENSITIVE_NAMES | EXCLUDED_DIR_PARTS),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Collect a safe, read-only Codex profile inventory as JSON."
    )
    parser.add_argument("--home", default=str(Path.home()), help="User home directory")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    profile = collect_profile(Path(args.home))
    indent = 2 if args.pretty else None
    print(json.dumps(profile, ensure_ascii=False, indent=indent, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
