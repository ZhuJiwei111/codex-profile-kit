#!/usr/bin/env python3
"""Audit, export, verify, push, and apply a portable Codex profile kit."""

from __future__ import annotations

import argparse
import filecmp
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HOME = Path.home()

MANAGED_DIRS = ("rules", "templates", "skills", "hooks")
MANAGED_FILES = ("INSTALL.md", "MIGRATION_MANIFEST.md", "CONNECTORS.md")
FORBIDDEN_NAMES = {
    "auth.json",
    "history.jsonl",
    "session_index.jsonl",
    "__pycache__",
}
FORBIDDEN_SUFFIXES = (".sqlite", ".sqlite-shm", ".sqlite-wal", ".pyc", ".tar.gz")
FORBIDDEN_PARTS = {
    "attachments",
    "cache",
    "memories",
    "sessions",
    "archived_sessions",
    ".tmp",
}
ALLOWED_SKILL_KEYS = {
    "allowed-tools",
    "description",
    "license",
    "metadata",
    "name",
}
PORTABLE_CODEX_SKILL_NAMES = {
    "awesome-rebuttal",
    "code-documentation",
    "code-simplifier",
    "context-save-restore",
    "hookify-writing-rules",
}
SAFE_AGENT_SECTIONS = {
    "Maintenance",
    "Workflow",
    "Long-Running Jobs",
    "Language",
    "Temporary Workspaces",
    "Security",
    "Ask First",
}


HOST_LOCAL_TEMPLATE = """# Host Local Overlay Template

Copy this file to `HOST_LOCAL.md` on the target machine and fill in only facts
that are true there. Do not copy secrets into this file.

## Host

- Home directory:
- Primary work root:
- OS:
- Default shell:
- Non-interactive shell startup behavior:
- Timezone for user-facing timestamps:
- Useful tools confirmed with `command -v`:

## Python And Conda

- Preferred Python command:
- Conda root:
- Project environment root:
- Conda package cache:
- Preferred package manager:
- User-site Python visibility policy:

## Proxy And Network

- Are proxy variables set by default:
- Proxy enable command:
- Proxy disable command:
- Direct-network test command for large downloads:
- Notes for package indexes or GitHub access:

## Storage And GPU

- Storage paths to check before large artifacts:
- Storage check command:
- GPU availability:
- CUDA home:
- CUDA version:
- Required GPU scoping convention:

## Local Install Decisions

- Which skills were installed:
- Were hooks enabled:
- Connectors re-authenticated:
- Date of last smoke test:
"""


CONFIG_TEMPLATE = """model = "gpt-5.5"
model_reasoning_effort = "xhigh"
sandbox_mode = "workspace-write"
personality = "friendly"
service_tier = "default"

[plugins."github@openai-curated"]
enabled = true

[features]
hooks = true

[sandbox_workspace_write]
network_access = true
"""


CONNECTORS = """# Connector Reconnection Checklist

Do not copy connector auth state, OAuth tokens, cookies, app caches, or plugin
caches from the source machine.

## GitHub Plugin

- Install or enable the GitHub plugin on the target machine.
- Re-authenticate through the target Codex UI or CLI flow.
- Verify repository access with a low-risk metadata read before using PR or
  issue workflows.

## Other Connectors

- Reinstall connectors from trusted sources on the target machine.
- Re-authenticate interactively.
- Keep credentials out of `AGENTS.md`, skills, hooks, templates, and migration
  reports.

## Smoke Check

Ask Codex to summarize available connector capabilities without printing secret
values. If a connector fails, repair the target-machine installation rather than
copying old state.
"""


INSTALL = """# Install Guide

This flow is template-based. Inspect each step before enabling hooks on the
target machine.

## 1. Clone

```bash
git clone https://github.com/ZhuJiwei111/codex-profile-kit.git
cd codex-profile-kit
python3 scripts/sync.py verify
```

## 2. Fill Host Facts

```bash
cp templates/HOST_LOCAL_TEMPLATE.md HOST_LOCAL.md
```

Fill `HOST_LOCAL.md` with target-machine facts. Keep secrets out of it.

## 3. Install Portable Rules

Review `rules/AGENTS.portable.md`, then merge it into the target
`~/.codex/AGENTS.md`. Add only true target-machine facts from `HOST_LOCAL.md`.

## 4. Dry-Run Apply

```bash
python3 scripts/sync.py apply
```

The default is dry-run. It reports changed portable assets and manual-review
areas without writing to active Codex configuration.

## 5. Apply After Review

```bash
python3 scripts/sync.py apply --confirm
```

The script backs up overwritten files under `~/codex-migration-archive/` before
copying portable skills, hooks, Hookify rules, hook docs, and rendered
`hooks.json`.

## 6. Reconnect Plugins

Use `CONNECTORS.md` as the checklist. Re-authenticate connectors on the target
machine instead of copying connector state.
"""


def run(cmd: list[str], cwd: Path = REPO_ROOT, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def rel(path: Path, root: Path = REPO_ROOT) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def copytree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def frontmatter_bounds(text: str) -> tuple[int, int] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    return 4, end


def parse_frontmatter(text: str) -> dict[str, str]:
    bounds = frontmatter_bounds(text)
    if bounds is None:
        return {}
    start, end = bounds
    data: dict[str, str] = {}
    for line in text[start:end].splitlines():
        if line.startswith((" ", "\t")):
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("-") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def sanitize_skill(skill_file: Path) -> None:
    text = skill_file.read_text(encoding="utf-8")
    bounds = frontmatter_bounds(text)
    if bounds is None:
        return
    start, end = bounds
    raw = text[start:end]
    kept = []
    for line in raw.splitlines():
        key = line.split(":", 1)[0].strip() if ":" in line else ""
        if key == "version":
            continue
        kept.append(line)
    sanitized = "---\n" + "\n".join(kept).rstrip() + "\n---" + text[end + 4 :]
    skill_file.write_text(sanitized, encoding="utf-8")


def is_portable_codex_skill(name: str) -> bool:
    return name.startswith("personal-") or name in PORTABLE_CODEX_SKILL_NAMES


def section_title(line: str) -> str | None:
    stripped = line.strip()
    if stripped.startswith("## ") and not stripped.startswith("### "):
        return stripped[3:].strip()
    return None


def extract_agent_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        title = section_title(line)
        if title:
            current = title
            sections[current] = [line]
        elif current:
            sections[current].append(line)
    return sections


def portable_agents(active_agents: Path) -> str:
    text = active_agents.read_text(encoding="utf-8")
    sections = extract_agent_sections(text)
    out = [
        "# Portable Codex Instructions",
        "",
        "These are durable, machine-neutral instructions for Codex sessions. Keep",
        "host-specific facts in `HOST_LOCAL.md`, not in this file. Project repositories",
        "may add narrower `AGENTS.md` files.",
        "",
    ]
    for title in (
        "Maintenance",
        "Workflow",
        "Long-Running Jobs",
        "Language",
        "Temporary Workspaces",
    ):
        if title in sections:
            out.extend(sections[title])
            out.append("")
    out.extend(
        [
            "## Host Overlay",
            "",
            "* Fill target-machine facts in `HOST_LOCAL.md` before relying on host-specific",
            "  assumptions.",
            "* Verify shell behavior, timezone, proxy commands, storage paths, GPU/CUDA",
            "  availability, and preferred Python/Conda locations on the target machine.",
            "* Prefer `python3` over `python` unless a conda or virtual environment is",
            "  active.",
            "* Verify less-common tools with `command -v` before relying on them.",
            "* Do not assume a graphical editor command exists; prefer non-interactive",
            "  commands.",
            "",
            "## Python And Conda",
            "",
            "* Keep the `base` conda environment minimal. Do not use `base` for project work",
            "  and do not install project packages into `base`.",
            "* Use project-specific environments. If the intended environment is unclear, ask",
            "  before installing packages.",
            "* Prefer `uv` for Python package and environment workflows when it fits the",
            "  project, but do not mix it into an unclear conda setup without checking first.",
            "* If a missing Python package would materially simplify the work, propose",
            "  installing it in the correct project environment.",
            "* Do not assume user-site Python packages are visible.",
            "",
            "## Proxy And Network",
            "",
            "* Avoid wasting proxy bandwidth. Before large downloads, datasets, models,",
            "  wheels, archives, or other high-traffic operations, test direct access with a",
            "  small request and prefer direct download when it works.",
            "* Small metadata queries, package index checks, GitHub access, and external docs",
            "  may use proxy when needed.",
            "* Ask before running package-manager operations that may fetch large dependency",
            "  trees.",
            "* If unsure whether a high-traffic task should use proxy, ask first.",
            "",
            "## Storage And GPU",
            "",
            "* Check available storage before creating or downloading large artifacts.",
            "* Check GPU availability before GPU work.",
            "* Use explicit GPU device scoping for heavy GPU jobs and ask first before heavy",
            "  GPU use.",
            "",
        ]
    )
    for title in ("Security", "Ask First"):
        if title in sections:
            out.extend(sections[title])
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def render_hooks_template(active_hooks_json: Path, home: Path) -> str:
    data = json.loads(active_hooks_json.read_text(encoding="utf-8"))
    home_text = str(home)

    def convert(value: object) -> object:
        if isinstance(value, dict):
            return {k: convert(v) for k, v in value.items()}
        if isinstance(value, list):
            return [convert(v) for v in value]
        if isinstance(value, str):
            value = value.replace(home_text, "{{HOME}}")
            value = re.sub(r"(^|\s)/usr/bin/python3(?=\s)", r"\1{{PYTHON3}}", value)
            value = re.sub(r"(^|\s)python3(?=\s)", r"\1{{PYTHON3}}", value)
            return value
        return value

    return json.dumps(convert(data), ensure_ascii=False, indent=2) + "\n"


def export_to(root: Path, home: Path, tarball: bool = False) -> None:
    codex = home / ".codex"
    agents = home / ".agents"
    for path in MANAGED_DIRS:
        target = root / path
        if target.exists():
            shutil.rmtree(target)
    for path in MANAGED_FILES:
        target = root / path
        if target.exists():
            target.unlink()

    (root / "rules").mkdir(parents=True, exist_ok=True)
    write_text(root / "rules" / "AGENTS.portable.md", portable_agents(codex / "AGENTS.md"))

    (root / "templates").mkdir(parents=True, exist_ok=True)
    write_text(root / "templates" / "HOST_LOCAL_TEMPLATE.md", HOST_LOCAL_TEMPLATE)
    write_text(root / "templates" / "config.toml.template", CONFIG_TEMPLATE)
    write_text(root / "templates" / "hooks.json.template", render_hooks_template(codex / "hooks.json", home))

    skills_root = root / "skills"
    (skills_root / "codex").mkdir(parents=True, exist_ok=True)
    for skill_dir in sorted((codex / "skills").iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            continue
        if not is_portable_codex_skill(skill_dir.name):
            continue
        dst = skills_root / "codex" / skill_dir.name
        copytree(skill_dir, dst)
        skill_file = dst / "SKILL.md"
        if skill_file.exists():
            sanitize_skill(skill_file)
    if (agents / "skills" / "find-skills").is_dir():
        copytree(agents / "skills" / "find-skills", skills_root / "agents" / "find-skills")

    hooks_root = root / "hooks"
    (hooks_root / "scripts").mkdir(parents=True, exist_ok=True)
    (hooks_root / "rules").mkdir(parents=True, exist_ok=True)
    (hooks_root / "docs").mkdir(parents=True, exist_ok=True)
    for path in sorted((codex / "hooks").glob("*.py")):
        shutil.copy2(path, hooks_root / "scripts" / path.name)
    smart_commit = codex / "hooks" / "smart-commit.md"
    if smart_commit.exists():
        text = smart_commit.read_text(encoding="utf-8").replace(str(home), "{{HOME}}")
        write_text(hooks_root / "docs" / "smart-commit.md", text)
    for path in sorted((codex / "hookify").glob("*.md")):
        shutil.copy2(path, hooks_root / "rules" / path.name)

    write_text(root / "CONNECTORS.md", CONNECTORS)
    write_text(root / "INSTALL.md", INSTALL)
    write_text(root / "MIGRATION_MANIFEST.md", migration_manifest())

    if tarball:
        archive = root.parent / f"{root.name}-{datetime.now().strftime('%Y%m%d')}.tar.gz"
        with tarfile.open(archive, "w:gz") as handle:
            handle.add(root, arcname=root.name, filter=tar_filter)
        print(f"wrote {archive}")


def tar_filter(info: tarfile.TarInfo) -> tarfile.TarInfo | None:
    parts = Path(info.name).parts
    if any(part in FORBIDDEN_PARTS or part in FORBIDDEN_NAMES for part in parts):
        return None
    if info.name.endswith(FORBIDDEN_SUFFIXES):
        return None
    if ".git" in parts:
        return None
    return info


def migration_manifest() -> str:
    return """# Migration Manifest

Generated for a clean Codex profile kit.

## Included

- `rules/AGENTS.portable.md`: machine-neutral durable Codex behavior rules.
- `templates/HOST_LOCAL_TEMPLATE.md`: target-machine overlay template.
- `templates/hooks.json.template`: Codex hook wiring template with placeholders.
- `templates/config.toml.template`: minimal portable Codex config reference.
- `skills/codex/`: personal workflow skills plus explicitly allowlisted
  portable Codex skills from `~/.codex/skills`.
- `skills/agents/find-skills/`: portable agent skill discovery helper.
- `hooks/scripts/`: hook scripts and tests from `~/.codex/hooks`.
- `hooks/rules/`: Hookify markdown rules from `~/.codex/hookify`.
- `hooks/docs/smart-commit.md`: smart-commit hook notes with templated paths.
- `CONNECTORS.md`: re-authentication checklist for plugins/connectors.
- `INSTALL.md`: target-machine install and smoke-test guide.

## Excluded

- Codex auth files, tokens, connector OAuth state, cookies, passwords, and
  secrets.
- Session history, archived sessions, logs, attachments, and pasted files.
- SQLite databases, WAL/SHM files, state databases, and goal/history stores.
- Codex memories and rollout summaries.
- Plugin caches, app caches, marketplace temporary clones, and model caches.
- Project trust lists, hook trusted hashes, approval history, and local runtime
  state.
- Conda environments, package caches, datasets, model weights, project outputs,
  and machine-specific tool installations.
"""


@dataclass
class DiffSummary:
    only_left: list[str]
    only_right: list[str]
    different: list[str]


def file_map(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel_path = path.relative_to(root).as_posix()
        if rel_path.startswith(".git/"):
            continue
        result[rel_path] = sha256(path)
    return result


def diff_dirs(left: Path, right: Path) -> DiffSummary:
    left_map = file_map(left)
    right_map = file_map(right)
    return DiffSummary(
        only_left=sorted(set(left_map) - set(right_map)),
        only_right=sorted(set(right_map) - set(left_map)),
        different=sorted(k for k in set(left_map) & set(right_map) if left_map[k] != right_map[k]),
    )


def print_diff(summary: DiffSummary) -> None:
    for label, values in (
        ("only_export", summary.only_left),
        ("only_repo", summary.only_right),
        ("different", summary.different),
    ):
        print(f"{label}: {len(values)}")
        for value in values[:80]:
            print(f"  {value}")
        if len(values) > 80:
            print(f"  ... +{len(values) - 80} more")


def forbidden_path(path: Path) -> bool:
    parts = set(path.parts)
    if path.name in FORBIDDEN_NAMES:
        return True
    if any(part in FORBIDDEN_PARTS for part in parts):
        return True
    return path.name.endswith(FORBIDDEN_SUFFIXES)


def scan_forbidden(root: Path) -> list[str]:
    bad: list[str] = []
    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        if forbidden_path(path):
            bad.append(rel(path, root))
    return sorted(bad)


def validate_skills(root: Path) -> None:
    skill_roots = [root / "skills" / "codex", root / "skills" / "agents"]
    for skill_root in skill_roots:
        if not skill_root.is_dir():
            continue
        for skill_dir in sorted(p for p in skill_root.iterdir() if p.is_dir()):
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.is_file():
                raise SystemExit(f"missing SKILL.md: {rel(skill_dir, root)}")
            text = skill_file.read_text(encoding="utf-8")
            fm = parse_frontmatter(text)
            if not fm.get("name") or not fm.get("description"):
                raise SystemExit(f"missing required frontmatter: {rel(skill_file, root)}")
            extra = set(fm) - ALLOWED_SKILL_KEYS
            if extra:
                raise SystemExit(f"unexpected frontmatter keys in {rel(skill_file, root)}: {sorted(extra)}")
            if fm["name"] != skill_dir.name:
                raise SystemExit(f"skill name/folder mismatch: {rel(skill_file, root)}")


def validate_hookify(root: Path) -> None:
    count = 0
    for path in sorted((root / "hooks" / "rules").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if "pattern" in fm:
            re.compile(fm["pattern"])
            count += 1
    print(f"hookify regex ok: {count}")


def validate_json(root: Path) -> None:
    template = root / "templates" / "hooks.json.template"
    text = template.read_text(encoding="utf-8")
    rendered = text.replace("{{HOME}}", "/tmp/codex-home").replace("{{PYTHON3}}", "python3")
    json.loads(rendered)


def validate_hooks(root: Path) -> None:
    scripts = sorted((root / "hooks" / "scripts").glob("*.py"))
    if scripts:
        cache = Path(tempfile.mkdtemp(prefix="codex-profile-pycache-"))
        try:
            result = run(["python3", "-X", f"pycache_prefix={cache}", "-m", "py_compile", *map(str, scripts)])
            if result.returncode:
                raise SystemExit(result.stderr or result.stdout)
        finally:
            shutil.rmtree(cache, ignore_errors=True)
    with tempfile.TemporaryDirectory(prefix="codex-profile-test-home-") as tmp_home:
        tmp_home_path = Path(tmp_home)
        rule_dst = tmp_home_path / ".codex" / "hookify"
        rule_dst.mkdir(parents=True)
        for rule in (root / "hooks" / "rules").glob("*.md"):
            shutil.copy2(rule, rule_dst / rule.name)
        env = os.environ.copy()
        env["HOME"] = str(tmp_home_path)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        for test_name in (
            "test_smart_commit_stage.py",
            "test_direct_download_guard.py",
            "test_hookify_codex_runner.py",
        ):
            test_path = root / "hooks" / "scripts" / test_name
            if not test_path.exists():
                continue
            result = run(["python3", str(test_path)], cwd=root, env=env)
            if result.returncode:
                raise SystemExit(result.stdout + result.stderr)


def verify_repo(root: Path = REPO_ROOT) -> None:
    bad = scan_forbidden(root)
    if bad:
        raise SystemExit("forbidden paths:\n" + "\n".join(bad))
    validate_skills(root)
    validate_hookify(root)
    validate_json(root)
    validate_hooks(root)
    print("profile kit verification ok")


def export_dry_run(home: Path) -> DiffSummary:
    with tempfile.TemporaryDirectory(prefix="codex-profile-export-") as tmp:
        tmp_root = Path(tmp) / REPO_ROOT.name
        shutil.copytree(REPO_ROOT, tmp_root, ignore=shutil.ignore_patterns(".git"))
        export_to(tmp_root, home)
        return diff_dirs(tmp_root, REPO_ROOT)


def cmd_audit(args: argparse.Namespace) -> int:
    summary = export_dry_run(Path(args.home))
    print_diff(summary)
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    home = Path(args.home)
    if args.dry_run:
        print_diff(export_dry_run(home))
        return 0
    export_to(REPO_ROOT, home, tarball=args.tarball)
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    verify_repo(REPO_ROOT)
    return 0


def cmd_push(args: argparse.Namespace) -> int:
    export_to(REPO_ROOT, Path(args.home))
    verify_repo(REPO_ROOT)
    status = run(["git", "status", "--short"])
    print(status.stdout, end="")
    if not args.confirm:
        print("push skipped: rerun with --confirm to commit and push")
        return 0
    if not status.stdout.strip():
        print("nothing to commit")
        return 0
    run(["git", "add", "-A"], check_git_cwd())
    message = args.message or f"Sync Codex profile kit {datetime.now().strftime('%Y-%m-%d')}"
    commit = run(["git", "commit", "-m", message])
    if commit.returncode:
        raise SystemExit(commit.stdout + commit.stderr)
    push = run(["git", "push", "-u", "origin", "main"])
    if push.returncode:
        raise SystemExit(push.stdout + push.stderr)
    print(push.stdout, end="")
    return 0


def check_git_cwd() -> Path:
    return REPO_ROOT


def copy_file_with_backup(src: Path, dst: Path, backup_root: Path) -> None:
    if dst.exists():
        backup = backup_root / dst.relative_to(Path.home())
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dst, backup)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def apply_pairs(home: Path) -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    for skill in (REPO_ROOT / "skills" / "codex").iterdir():
        if skill.is_dir():
            pairs.append((skill, home / ".codex" / "skills" / skill.name))
    for skill in (REPO_ROOT / "skills" / "agents").iterdir():
        if skill.is_dir():
            pairs.append((skill, home / ".agents" / "skills" / skill.name))
    for path in (REPO_ROOT / "hooks" / "rules").glob("*.md"):
        pairs.append((path, home / ".codex" / "hookify" / path.name))
    for path in (REPO_ROOT / "hooks" / "scripts").glob("*.py"):
        pairs.append((path, home / ".codex" / "hooks" / path.name))
    smart = REPO_ROOT / "hooks" / "docs" / "smart-commit.md"
    if smart.exists():
        pairs.append((smart, home / ".codex" / "hooks" / "smart-commit.md"))
    return pairs


def cmd_apply(args: argparse.Namespace) -> int:
    home = Path(args.home)
    verify_repo(REPO_ROOT)
    changed: list[str] = []
    for src, dst in apply_pairs(home):
        if not dst.exists() or (src.is_file() and sha256(src) != sha256(dst)):
            changed.append(f"{rel(src)} -> {dst}")
        elif src.is_dir():
            diff = filecmp.dircmp(src, dst)
            if diff.left_only or diff.right_only or diff.diff_files:
                changed.append(f"{rel(src)} -> {dst}")
    hooks_template = (REPO_ROOT / "templates" / "hooks.json.template").read_text(encoding="utf-8")
    rendered_hooks = hooks_template.replace("{{HOME}}", str(home)).replace("{{PYTHON3}}", "/usr/bin/python3")
    hooks_dst = home / ".codex" / "hooks.json"
    if not hooks_dst.exists() or hooks_dst.read_text(encoding="utf-8") != rendered_hooks:
        changed.append(f"templates/hooks.json.template -> {hooks_dst}")

    print("manual review only: rules/AGENTS.portable.md and templates/config.toml.template")
    print(f"changed portable targets: {len(changed)}")
    for item in changed[:100]:
        print(f"  {item}")
    if len(changed) > 100:
        print(f"  ... +{len(changed) - 100} more")
    if not args.confirm:
        print("dry-run only: rerun with --confirm to apply")
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = home / "codex-migration-archive" / f"{stamp}-before-profile-kit-apply"
    backup_root.mkdir(parents=True, exist_ok=True)
    for src, dst in apply_pairs(home):
        if src.is_dir():
            if dst.exists():
                backup = backup_root / dst.relative_to(home)
                backup.parent.mkdir(parents=True, exist_ok=True)
                copytree(dst, backup)
            copytree(src, dst)
        else:
            copy_file_with_backup(src, dst, backup_root)
    copy_file_with_backup(REPO_ROOT / "templates" / "hooks.json.template", backup_root / "rendered-hooks-template.txt", backup_root)
    hooks_dst.parent.mkdir(parents=True, exist_ok=True)
    if hooks_dst.exists():
        backup = backup_root / hooks_dst.relative_to(home)
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(hooks_dst, backup)
    hooks_dst.write_text(rendered_hooks, encoding="utf-8")
    print(f"applied; backup: {backup_root}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", default=str(DEFAULT_HOME), help="active profile home")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("audit").set_defaults(func=cmd_audit)
    export = sub.add_parser("export")
    export.add_argument("--dry-run", action="store_true")
    export.add_argument("--tarball", action="store_true")
    export.set_defaults(func=cmd_export)
    sub.add_parser("verify").set_defaults(func=cmd_verify)
    push = sub.add_parser("push")
    push.add_argument("--confirm", action="store_true")
    push.add_argument("-m", "--message")
    push.set_defaults(func=cmd_push)
    apply = sub.add_parser("apply")
    apply.add_argument("--confirm", action="store_true")
    apply.set_defaults(func=cmd_apply)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
