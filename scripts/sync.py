#!/usr/bin/env python3
"""Audit, export, verify, and apply the portable Codex profile kit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import stat
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HOME = Path.home()

HOOK_SCRIPT_FILES = (
    "direct_download_guard.py",
    "local_safety_guard.py",
    "no_autoresolution_guard.py",
    "test_direct_download_guard.py",
    "test_hooks_configuration.py",
    "test_local_safety_guard.py",
    "test_no_autoresolution_guard.py",
)
MANAGED_ROOTS = ("rules", "templates", "skills", "hooks")
RETIRED_PERSONAL_SKILLS = frozenset({"personal-review-response"})
RETIRED_ACTIVE_PATHS = (
    Path(".codex/skills/personal-review-response"),
    Path(".codex/agents/monitor.toml"),
    Path(".codex/agents/reviewer.toml"),
    Path(".codex/hookify/README.md"),
    Path(".codex/hookify/block-base-conda-install.md"),
    Path(".codex/hookify/block-sensitive-file-edits.md"),
    Path(".codex/hookify/block-sensitive-path-command.md"),
    Path(".codex/hooks/hookify_codex_runner.py"),
    Path(".codex/hooks/test_hookify_codex_runner.py"),
)
RETIRED_REPO_PATHS = (
    Path("skills/codex/personal-review-response"),
    Path("agents/codex/monitor.toml"),
    Path("agents/codex/reviewer.toml"),
    Path("hooks/rules"),
    Path("hooks/scripts/hookify_codex_runner.py"),
    Path("hooks/scripts/test_hookify_codex_runner.py"),
)
PORTABLE_FORBIDDEN_DIRECTORIES = {
    ".cache",
    ".git",
    ".hg",
    ".ssh",
    ".svn",
    ".tmp",
    "__pycache__",
    "archived_sessions",
    "attachments",
    "cache",
    "logs",
    "memories",
    "runtime",
    "sessions",
}
PORTABLE_SENSITIVE_NAMES = {
    ".env",
    ".netrc",
    "auth.json",
    "config.toml",
    "credentials.json",
    "credentials.toml",
    "credentials.yaml",
    "credentials.yml",
    "history.jsonl",
    "host_local.md",
    "secrets.json",
    "secrets.toml",
    "secrets.yaml",
    "secrets.yml",
    "session_index.jsonl",
}
PORTABLE_PRIVATE_KEY_SUFFIXES = (
    ".jks",
    ".key",
    ".p12",
    ".pem",
    ".pfx",
    ".ppk",
)
PORTABLE_RUNTIME_SUFFIXES = (
    ".cache",
    ".log",
    ".pyc",
    ".sqlite",
    ".sqlite-shm",
    ".sqlite-wal",
    ".tar.gz",
)
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


@dataclass(frozen=True)
class ManagedEntry:
    destination: Path
    source: Path | None = None
    content: bytes | None = None
    mode: int | None = None
    label: str = "managed content"
    delete: bool = False

    def is_directory(self) -> bool:
        return self.source is not None and self.source.is_dir()


@dataclass(frozen=True)
class Drift:
    state: str
    label: str
    destination: Path


@dataclass
class AppliedEntry:
    destination: Path
    stage: Path | None
    hold: Path | None


class RollbackError(RuntimeError):
    def __init__(
        self,
        original: BaseException,
        failures: list[tuple[str, tuple[Path, ...], BaseException]],
        backup_root: Path | None,
    ) -> None:
        lines = [
            f"rollback failed after {type(original).__name__}; manual recovery is required"
        ]
        for action, paths, error in failures:
            rendered_paths = " -> ".join(str(path) for path in paths)
            lines.append(f"  {action}: {rendered_paths} ({type(error).__name__})")
        if backup_root is not None and path_lexists(backup_root):
            lines.append(f"  recovery backup retained: {backup_root}")
        super().__init__("\n".join(lines))


def path_lexists(path: Path) -> bool:
    return os.path.lexists(path)


def rel(path: Path, root: Path = REPO_ROOT) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def is_portable_codex_skill(name: str) -> bool:
    return name.startswith("personal-")


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
    parsed: dict[str, str] = {}
    for line in text[start:end].splitlines():
        if line.startswith((" ", "\t")) or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key and not key.startswith("#"):
            parsed[key] = value.strip().strip('"').strip("'")
    return parsed


def _mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_regular_path(path: Path, *, label: str) -> None:
    if not path_lexists(path):
        raise RuntimeError(f"{label} is unavailable: {path}")
    root_mode = path.lstat().st_mode
    if stat.S_ISLNK(root_mode):
        raise RuntimeError(f"{label} must not be a symbolic link: {path}")
    if stat.S_ISREG(root_mode):
        return
    if not stat.S_ISDIR(root_mode):
        raise RuntimeError(f"{label} contains a special file: {path}")
    for current, directories, files in os.walk(path, followlinks=False):
        current_path = Path(current)
        for name in directories:
            child = current_path / name
            child_mode = child.lstat().st_mode
            if stat.S_ISLNK(child_mode):
                raise RuntimeError(
                    f"{label} contains a symbolic link: {child}"
                )
            if not stat.S_ISDIR(child_mode):
                raise RuntimeError(f"{label} contains a special file: {child}")
        for name in files:
            child = current_path / name
            child_mode = child.lstat().st_mode
            if stat.S_ISLNK(child_mode):
                raise RuntimeError(f"{label} contains a symbolic link: {child}")
            if not stat.S_ISREG(child_mode):
                raise RuntimeError(f"{label} contains a special file: {child}")


def _tree_signature(path: Path) -> tuple[tuple[str, str, int, str], ...]:
    validate_regular_path(path, label="managed tree")
    if path.is_file():
        return ((".", "file", _mode(path), _sha256(path)),)
    rows: list[tuple[str, str, int, str]] = [(".", "dir", _mode(path), "")]
    for current, directories, files in os.walk(path, followlinks=False):
        directories.sort()
        files.sort()
        current_path = Path(current)
        for name in directories:
            child = current_path / name
            rows.append((child.relative_to(path).as_posix(), "dir", _mode(child), ""))
        for name in files:
            child = current_path / name
            rows.append(
                (
                    child.relative_to(path).as_posix(),
                    "file",
                    _mode(child),
                    _sha256(child),
                )
            )
    return tuple(rows)


def _entry_matches(entry: ManagedEntry) -> bool:
    destination = entry.destination
    if not path_lexists(destination):
        return entry.delete
    if destination.is_symlink():
        raise RuntimeError(f"managed destination must not be a symbolic link: {destination}")
    if entry.delete:
        validate_regular_path(destination, label="retired managed destination")
        return False
    if entry.content is not None:
        if not destination.is_file():
            return False
        desired_mode = entry.mode if entry.mode is not None else 0o644
        return destination.read_bytes() == entry.content and _mode(destination) == desired_mode
    if entry.source is None:
        raise RuntimeError(f"managed entry has no source: {entry.label}")
    validate_regular_path(entry.source, label="managed source")
    if entry.source.is_dir() != destination.is_dir():
        return False
    if entry.source.is_file() != destination.is_file():
        return False
    return _tree_signature(entry.source) == _tree_signature(destination)


def _reject_symlink_components(path: Path) -> None:
    absolute = Path(os.path.abspath(path))
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if current.is_symlink():
            raise RuntimeError(f"path component must not be a symbolic link: {current}")


def normalized_home(home: Path) -> Path:
    result = Path(os.path.abspath(home.expanduser()))
    if result == Path(result.anchor):
        raise RuntimeError(f"target home must not be the filesystem root: {result}")
    _reject_symlink_components(result)
    if not result.is_dir():
        raise RuntimeError(f"target home must be an existing directory: {result}")
    return result


def safe_scoped_path(path: Path, base: Path, *, label: str) -> Path:
    base = Path(os.path.abspath(base))
    target = Path(os.path.abspath(path))
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise RuntimeError(f"{label} escapes managed root {base}: {target}") from exc
    _reject_symlink_components(base)
    current = base
    for part in target.relative_to(base).parts:
        current /= part
        if current.is_symlink():
            raise RuntimeError(f"{label} contains a symbolic-link component: {current}")
    return target


def _portable_path_forbidden_reason(path: Path, portable_root: Path) -> str | None:
    relative = path.relative_to(portable_root)
    lowered_parts = tuple(part.casefold() for part in relative.parts)
    if any(part in PORTABLE_FORBIDDEN_DIRECTORIES for part in lowered_parts):
        return "forbidden directory"
    name = lowered_parts[-1]
    if name in PORTABLE_SENSITIVE_NAMES or name.startswith(".env."):
        return "sensitive file"
    if name.endswith(PORTABLE_PRIVATE_KEY_SUFFIXES):
        return "private-key file"
    if name.endswith(PORTABLE_RUNTIME_SUFFIXES):
        return "runtime file"
    return None


def validate_managed_snapshot_paths(root: Path) -> None:
    errors: list[str] = []
    for name in MANAGED_ROOTS:
        managed_root = root / name
        if not path_lexists(managed_root):
            continue
        if managed_root.is_symlink():
            errors.append(f"managed root is a symbolic link: {managed_root}")
            continue
        if not managed_root.is_dir():
            errors.append(f"managed root is not a directory: {managed_root}")
            continue
        for current, directories, files in os.walk(managed_root, followlinks=False):
            current_path = Path(current)
            for child_name in directories:
                child = current_path / child_name
                child_mode = child.lstat().st_mode
                if stat.S_ISLNK(child_mode):
                    errors.append(f"managed profile contains symbolic link: {child}")
                elif not stat.S_ISDIR(child_mode):
                    errors.append(f"managed profile contains special file: {child}")
                reason = _portable_path_forbidden_reason(child, managed_root)
                if reason:
                    errors.append(
                        f"forbidden portable path ({reason}): "
                        f"{child.relative_to(managed_root).as_posix()}"
                    )
            for child_name in files:
                child = current_path / child_name
                child_mode = child.lstat().st_mode
                if stat.S_ISLNK(child_mode):
                    errors.append(f"managed profile contains symbolic link: {child}")
                elif not stat.S_ISREG(child_mode):
                    errors.append(f"managed profile contains special file: {child}")
                reason = _portable_path_forbidden_reason(child, managed_root)
                if reason:
                    errors.append(
                        f"forbidden portable path ({reason}): "
                        f"{child.relative_to(managed_root).as_posix()}"
                    )
    if errors:
        raise SystemExit("unsafe managed profile:\n" + "\n".join(sorted(errors)))


def _local_link_target(raw_target: str) -> str | None:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]
    target = target.split("#", 1)[0].split("?", 1)[0]
    if not target or target.startswith("#"):
        return None
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
        return None
    return target


def validate_skill_resource_links(skill_dir: Path, root: Path) -> None:
    skill_root = skill_dir.resolve(strict=True)
    for markdown in sorted(skill_dir.rglob("*.md")):
        if markdown.name == "source-notes.md":
            continue
        if markdown.is_symlink():
            raise SystemExit(f"skill resource is a symbolic link: {rel(markdown, root)}")
        text = markdown.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK_RE.finditer(text):
            raw_target = _local_link_target(match.group(1))
            if raw_target is None:
                continue
            if Path(raw_target).is_absolute():
                raise SystemExit(
                    f"skill resource link escapes skill: {rel(markdown, root)} -> {raw_target}"
                )
            target = (markdown.parent / raw_target).resolve(strict=False)
            try:
                target.relative_to(skill_root)
            except ValueError as exc:
                raise SystemExit(
                    f"skill resource link escapes skill: {rel(markdown, root)} -> {raw_target}"
                ) from exc
            if not target.exists():
                raise SystemExit(
                    f"missing skill resource link: {rel(markdown, root)} -> {raw_target}"
                )


def validate_personal_skill_openai_yaml(skill_dir: Path, root: Path) -> None:
    path = skill_dir / "agents" / "openai.yaml"
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"missing personal skill openai.yaml: {rel(path, root)}")
    text = path.read_text(encoding="utf-8")
    if re.search(r"^interface:\s*$", text, re.MULTILINE) is None:
        raise SystemExit(f"missing openai interface: {rel(path, root)}")
    values: dict[str, str] = {}
    for key in ("display_name", "short_description", "default_prompt"):
        match = re.search(rf"^\s+{key}:\s*(.+?)\s*$", text, re.MULTILINE)
        if match is None:
            raise SystemExit(f"missing openai interface key {key}: {rel(path, root)}")
        values[key] = match.group(1).strip().strip('"').strip("'")
        if not values[key]:
            raise SystemExit(f"empty openai interface key {key}: {rel(path, root)}")
    if f"${skill_dir.name}" not in values["default_prompt"]:
        raise SystemExit(f"default_prompt does not name ${skill_dir.name}: {rel(path, root)}")
    policy = re.search(
        r"^policy:\s*$\n(?:^[ \t]+.*\n)*?^\s{2}allow_implicit_invocation:\s*(true|false)\s*$",
        text,
        re.MULTILINE,
    )
    if policy is None:
        raise SystemExit(
            f"missing boolean allow_implicit_invocation policy: {rel(path, root)}"
        )
    allow_implicit = policy.group(1) == "true"
    skill_frontmatter = parse_frontmatter(
        (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    )
    if skill_frontmatter.get("description", "").casefold().startswith("manual only"):
        if allow_implicit:
            raise SystemExit(
                f"manual-only skill must disable implicit invocation: {rel(path, root)}"
            )


def validate_skills(root: Path) -> None:
    codex_root = root / "skills" / "codex"
    if not codex_root.is_dir() or codex_root.is_symlink():
        raise SystemExit(f"missing skills/codex directory: {codex_root}")
    for item in sorted(codex_root.iterdir()):
        if not item.name.startswith("personal-"):
            raise SystemExit(f"non-personal Codex skill is not portable: {rel(item, root)}")
        if item.is_symlink() or not item.is_dir():
            raise SystemExit(f"personal skill must be a regular directory: {rel(item, root)}")
        skill_file = item / "SKILL.md"
        if not skill_file.is_file() or skill_file.is_symlink():
            raise SystemExit(f"missing SKILL.md: {rel(skill_file, root)}")
        frontmatter = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
        if frontmatter.get("name") != item.name:
            raise SystemExit(f"skill name/folder mismatch: {rel(skill_file, root)}")
        if not frontmatter.get("description"):
            raise SystemExit(f"missing skill description: {rel(skill_file, root)}")
        validate_personal_skill_openai_yaml(item, root)
        validate_skill_resource_links(item, root)
    agents_root = root / "skills" / "agents"
    if path_lexists(agents_root):
        if agents_root.is_symlink() or not agents_root.is_dir():
            raise SystemExit(f"skills/agents must be an empty directory: {agents_root}")
        contents = sorted(item.name for item in agents_root.iterdir())
        if contents:
            raise SystemExit(f"skills/agents content is unmanaged: {contents}")


def _validate_exact_inventory(path: Path, expected: Iterable[str], *, label: str) -> None:
    if not path.is_dir() or path.is_symlink():
        raise SystemExit(f"missing {label} inventory directory: {path}")
    expected_names = set(expected)
    observed = {item.name for item in path.iterdir()}
    if observed != expected_names:
        raise SystemExit(
            f"{label} inventory mismatch: expected={sorted(expected_names)} "
            f"observed={sorted(observed)}"
        )
    for name in expected_names:
        item = path / name
        if item.is_symlink() or not item.is_file():
            raise SystemExit(f"{label} inventory entry is not a regular file: {item}")


def validate_explicit_inventory(root: Path) -> None:
    _validate_exact_inventory(
        root / "hooks" / "scripts", HOOK_SCRIPT_FILES, label="hook script"
    )


def validate_retired_repo_paths(root: Path) -> None:
    present = [path for path in RETIRED_REPO_PATHS if path_lexists(root / path)]
    if present:
        rendered = ", ".join(path.as_posix() for path in present)
        raise SystemExit(f"retired profile artifacts must be absent: {rendered}")


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid JSON: {path}: {exc}") from exc


def _load_toml(path: Path) -> dict[str, object]:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise SystemExit(f"invalid TOML: {path}: {exc}") from exc


def validate_serialized_files(root: Path) -> None:
    for managed_name in MANAGED_ROOTS:
        managed_root = root / managed_name
        if not managed_root.is_dir():
            continue
        for path in sorted(managed_root.rglob("*.json")):
            _load_json(path)
        for path in sorted(managed_root.rglob("*.toml")):
            _load_toml(path)
    config_template = root / "templates" / "config.toml.template"
    if not config_template.is_file() or config_template.is_symlink():
        raise SystemExit(f"missing config template: {config_template}")
    _load_toml(config_template)
    hooks_template = root / "templates" / "hooks.json.template"
    if not hooks_template.is_file() or hooks_template.is_symlink():
        raise SystemExit(f"missing hooks template: {hooks_template}")
    rendered = hooks_template.read_text(encoding="utf-8").replace(
        "{{HOME}}", "/tmp/profile-home"
    ).replace("{{PYTHON3}}", "/usr/bin/python3")
    try:
        json.loads(rendered)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid rendered hooks template: {exc}") from exc


def verify_repo(root: Path = REPO_ROOT) -> None:
    validate_managed_snapshot_paths(root)
    agents = root / "rules" / "AGENTS.portable.md"
    if not agents.is_file() or agents.is_symlink():
        raise SystemExit(f"missing portable AGENTS file: {agents}")
    validate_retired_repo_paths(root)
    validate_skills(root)
    validate_explicit_inventory(root)
    validate_serialized_files(root)
    print("profile kit verification ok")


def _personal_skill_directories(root: Path) -> list[Path]:
    skill_root = root / "skills" / "codex"
    if not skill_root.is_dir():
        return []
    return sorted(
        item
        for item in skill_root.iterdir()
        if item.is_dir()
        and not item.is_symlink()
        and is_portable_codex_skill(item.name)
        and item.name not in RETIRED_PERSONAL_SKILLS
    )


def _source_apply_pairs(root: Path, home: Path) -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = [
        (root / "rules" / "AGENTS.portable.md", home / ".codex" / "AGENTS.md")
    ]
    pairs.extend(
        (skill, home / ".codex" / "skills" / skill.name)
        for skill in _personal_skill_directories(root)
    )
    pairs.extend(
        (root / "hooks" / "scripts" / name, home / ".codex" / "hooks" / name)
        for name in HOOK_SCRIPT_FILES
    )
    return pairs


def apply_pairs(home: Path) -> list[tuple[Path, Path]]:
    return _source_apply_pairs(REPO_ROOT, home)


def _render_hooks(root: Path, home: Path) -> bytes:
    text = (root / "templates" / "hooks.json.template").read_text(encoding="utf-8")
    home_fragment = json.dumps(shlex.quote(str(home)))[1:-1]
    python_fragment = json.dumps(shlex.quote("/usr/bin/python3"))[1:-1]
    text = text.replace("{{HOME}}", home_fragment).replace(
        "{{PYTHON3}}", python_fragment
    )
    json.loads(text)
    return text.encode("utf-8")


def managed_apply_entries(root: Path, home: Path) -> list[ManagedEntry]:
    entries = [
        ManagedEntry(destination=dst, source=src, label=rel(src, root))
        for src, dst in _source_apply_pairs(root, home)
    ]
    entries.append(
        ManagedEntry(
            destination=home / ".codex" / "hooks.json",
            content=_render_hooks(root, home),
            mode=0o600,
            label="templates/hooks.json.template (rendered)",
        )
    )
    entries.extend(
        ManagedEntry(
            destination=home / relative,
            label=f"retired profile artifact: {relative.as_posix()}",
            delete=True,
        )
        for relative in RETIRED_ACTIVE_PATHS
    )
    return entries


def validate_entry_plan(base: Path, entries: Iterable[ManagedEntry]) -> None:
    targets: list[Path] = []
    for entry in entries:
        target = safe_scoped_path(entry.destination, base, label="managed destination")
        if entry.delete:
            if entry.source is not None or entry.content is not None:
                raise RuntimeError(f"retired entry must not have replacement content: {entry.label}")
        elif entry.content is None:
            if entry.source is None:
                raise RuntimeError(f"managed entry lacks a source: {entry.label}")
            validate_regular_path(entry.source, label="managed source")
        elif entry.source is not None:
            raise RuntimeError(f"managed entry has both source and content: {entry.label}")
        targets.append(target)
    ordered = sorted(targets, key=lambda path: (len(path.parts), str(path)))
    if len(set(ordered)) != len(ordered):
        raise RuntimeError("managed destinations contain duplicates")
    for index, target in enumerate(ordered):
        for other in ordered[index + 1 :]:
            if target in other.parents:
                raise RuntimeError(
                    f"managed destinations overlap unsafely: {target} and {other}"
                )


def _ensure_parent_directories(path: Path, base: Path) -> list[Path]:
    parent = safe_scoped_path(path.parent, base, label="managed destination parent")
    created: list[Path] = []
    current = base
    for part in parent.relative_to(base).parts:
        current /= part
        if path_lexists(current):
            if current.is_symlink() or not current.is_dir():
                raise RuntimeError(f"managed destination parent is unsafe: {current}")
            continue
        current.mkdir()
        created.append(current)
    return created


def _remove_path(path: Path) -> None:
    if not path_lexists(path):
        return
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def _copy_regular_path(source: Path, destination: Path) -> None:
    validate_regular_path(source, label="managed source")
    if source.is_dir():
        shutil.copytree(source, destination, symlinks=False)
    else:
        shutil.copy2(source, destination)


def _stage_entry(entry: ManagedEntry) -> Path:
    if entry.delete:
        raise RuntimeError(f"retired entry must not be staged: {entry.label}")
    parent = entry.destination.parent
    stage: Path | None = None
    try:
        if entry.is_directory():
            stage = Path(
                tempfile.mkdtemp(
                    prefix=f".{entry.destination.name}.stage-", dir=parent
                )
            )
            stage.rmdir()
            assert entry.source is not None
            _copy_regular_path(entry.source, stage)
            return stage
        descriptor, raw_path = tempfile.mkstemp(
            prefix=f".{entry.destination.name}.stage-", dir=parent
        )
        os.close(descriptor)
        stage = Path(raw_path)
        if entry.content is not None:
            stage.write_bytes(entry.content)
            os.chmod(stage, entry.mode if entry.mode is not None else 0o644)
        else:
            assert entry.source is not None
            _copy_regular_path(entry.source, stage)
        return stage
    except BaseException as original:
        if stage is not None:
            try:
                _remove_path(stage)
            except BaseException as cleanup_error:
                raise RuntimeError(
                    f"staging failed and partial stage cleanup failed: {stage}"
                ) from original
        raise


def _unused_adjacent_path(destination: Path, marker: str) -> Path:
    path = Path(tempfile.mkdtemp(prefix=f".{destination.name}.{marker}-", dir=destination.parent))
    path.rmdir()
    return path


def promote_staged_path(stage: Path, destination: Path) -> None:
    os.replace(stage, destination)


def _ensure_private_directories(path: Path, home: Path) -> None:
    target = safe_scoped_path(path, home, label="apply backup directory")
    current = home
    for part in target.relative_to(home).parts:
        current /= part
        if path_lexists(current):
            if current.is_symlink() or not current.is_dir():
                raise RuntimeError(f"apply backup directory is unsafe: {current}")
        else:
            current.mkdir(mode=0o700)
        os.chmod(current, 0o700)


def _backup_entries(entries: list[ManagedEntry], backup_root: Path, home: Path) -> None:
    safe_scoped_path(backup_root, home, label="apply backup root")
    _ensure_private_directories(backup_root, home)
    manifest: list[dict[str, str]] = []
    for entry in entries:
        source = safe_scoped_path(
            entry.destination, home, label="backup source"
        )
        relative = entry.destination.relative_to(home)
        record = {"target": relative.as_posix(), "state": "missing"}
        if path_lexists(source):
            validate_regular_path(source, label="backup source")
            backup = backup_root / relative
            _ensure_private_directories(backup.parent, home)
            safe_scoped_path(backup, home, label="backup destination")
            _copy_regular_path(source, backup)
            record["state"] = "backed-up"
        manifest.append(record)
    manifest_path = backup_root / "manifest.json"
    safe_scoped_path(manifest_path, home, label="backup destination")
    descriptor, raw_stage = tempfile.mkstemp(prefix=".manifest.stage-", dir=backup_root)
    stage = Path(raw_stage)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump({"managed_targets": manifest}, handle, indent=2)
            handle.write("\n")
        os.chmod(stage, 0o600)
        safe_scoped_path(manifest_path, home, label="backup destination")
        os.replace(stage, manifest_path)
        os.chmod(manifest_path, 0o600)
    except BaseException:
        _remove_path(stage)
        raise


def _cleanup_created_directories(paths: Iterable[Path]) -> None:
    for path in sorted(set(paths), key=lambda item: len(item.parts), reverse=True):
        try:
            path.rmdir()
        except OSError:
            pass


def transactional_replace(
    entries: list[ManagedEntry],
    *,
    base: Path,
    backup_root: Path | None = None,
    post_check: Callable[[], None] | None = None,
) -> None:
    validate_entry_plan(base, entries)
    created: list[Path] = []
    staged: list[tuple[ManagedEntry, Path]] = []
    applied: list[AppliedEntry] = []
    backup_attempted = False
    try:
        for entry in entries:
            if not entry.delete:
                created.extend(_ensure_parent_directories(entry.destination, base))
        for entry in entries:
            safe_scoped_path(
                entry.destination, base, label="staging destination"
            )
            if entry.delete:
                continue
            if entry.source is not None:
                validate_regular_path(entry.source, label="managed source")
            staged.append((entry, _stage_entry(entry)))
        if backup_root is not None:
            backup_attempted = True
            _backup_entries(entries, backup_root, base)
        staged_by_destination = {entry.destination: stage for entry, stage in staged}
        for entry in entries:
            stage = staged_by_destination.get(entry.destination)
            hold: Path | None = None
            if path_lexists(entry.destination):
                hold = _unused_adjacent_path(entry.destination, "rollback")
                safe_scoped_path(hold, base, label="hold destination")
                safe_scoped_path(
                    entry.destination, base, label="hold source"
                )
                os.replace(entry.destination, hold)
            record = AppliedEntry(entry.destination, stage, hold)
            applied.append(record)
            if entry.delete:
                continue
            assert stage is not None
            safe_scoped_path(stage, base, label="promotion source")
            safe_scoped_path(
                entry.destination, base, label="promotion destination"
            )
            promote_staged_path(stage, entry.destination)
        if post_check is not None:
            post_check()
    except BaseException as original:
        rollback_failures: list[
            tuple[str, tuple[Path, ...], BaseException]
        ] = []
        for record in reversed(applied):
            try:
                safe_scoped_path(
                    record.destination, base, label="rollback destination"
                )
                _remove_path(record.destination)
            except BaseException as error:
                rollback_failures.append(
                    ("remove failed destination", (record.destination,), error)
                )
            if record.hold is not None and path_lexists(record.hold):
                try:
                    safe_scoped_path(record.hold, base, label="rollback hold")
                    safe_scoped_path(
                        record.destination, base, label="rollback destination"
                    )
                    os.replace(record.hold, record.destination)
                except BaseException as error:
                    rollback_failures.append(
                        (
                            "restore held destination",
                            (record.hold, record.destination),
                            error,
                        )
                    )
        for _, stage in staged:
            try:
                _remove_path(stage)
            except BaseException as error:
                rollback_failures.append(("remove staged path", (stage,), error))
        if backup_attempted and backup_root is not None and not rollback_failures:
            try:
                _remove_path(backup_root)
                try:
                    backup_root.parent.rmdir()
                except OSError:
                    pass
            except BaseException as error:
                rollback_failures.append(
                    ("remove failed transaction backup", (backup_root,), error)
                )
        _cleanup_created_directories(created)
        if rollback_failures:
            raise RollbackError(
                original,
                rollback_failures,
                backup_root if backup_attempted else None,
            ) from original
        raise
    for record in applied:
        if record.hold is not None:
            _remove_path(record.hold)
    for _, stage in staged:
        _remove_path(stage)


def _new_backup_root(home: Path) -> Path:
    archive = home / "codex-migration-archive"
    safe_scoped_path(archive, home, label="apply backup archive")
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S.%f")
    candidate = archive / f"{stamp}-before-profile-kit-apply"
    counter = 0
    while path_lexists(candidate):
        counter += 1
        candidate = archive / f"{stamp}-{counter}-before-profile-kit-apply"
    return candidate


def inbound_managed_drift(root: Path, home: Path) -> list[Drift]:
    entries = managed_apply_entries(root, home)
    validate_entry_plan(home, entries)
    drift: list[Drift] = []
    for entry in entries:
        if _entry_matches(entry):
            continue
        if entry.delete:
            state = "retired-present"
        else:
            state = "missing" if not path_lexists(entry.destination) else "different"
        drift.append(Drift(state, entry.label, entry.destination))
    return drift


def host_only_personal_skills(root: Path, home: Path) -> list[str]:
    repo_names = {path.name for path in _personal_skill_directories(root)}
    skill_root = home / ".codex" / "skills"
    if not path_lexists(skill_root):
        return []
    safe_scoped_path(skill_root, home, label="active personal skill root")
    if not skill_root.is_dir():
        raise RuntimeError(f"active personal skill root is not a directory: {skill_root}")
    additions: list[str] = []
    for item in sorted(skill_root.iterdir()):
        if not is_portable_codex_skill(item.name):
            continue
        if item.name in RETIRED_PERSONAL_SKILLS:
            continue
        validate_regular_path(item, label="active personal skill")
        if not item.is_dir():
            raise RuntimeError(f"active personal skill is not a directory: {item}")
        if item.name not in repo_names:
            additions.append(item.name)
    return additions


def _print_inbound(drift: list[Drift], additions: list[str]) -> None:
    print(f"inbound managed drift: {len(drift)}")
    for item in drift:
        print(f"  {item.state}: {item.label} -> {item.destination}")
    print(f"host-only personal additions: {len(additions)}")
    for name in additions:
        print(f"  {name}")


def apply_profile(root: Path, home: Path, *, confirm: bool) -> Path | None:
    verify_repo(root)
    home = normalized_home(home)
    entries = managed_apply_entries(root, home)
    validate_entry_plan(home, entries)
    changed = [entry for entry in entries if not _entry_matches(entry)]
    print(f"changed managed targets: {len(changed)}")
    for entry in changed:
        print(f"  {entry.label} -> {entry.destination}")
    if not confirm:
        print(
            "dry-run only: this describes the current state; "
            "--confirm rechecks identity and recomputes targets"
        )
        return None
    if not changed:
        print("no managed changes; no backup created")
        return None
    backup_root = _new_backup_root(home)

    def post_check() -> None:
        remaining = inbound_managed_drift(root, home)
        if remaining:
            raise RuntimeError(f"post-apply managed drift remains: {len(remaining)}")

    transactional_replace(
        changed,
        base=home,
        backup_root=backup_root,
        post_check=post_check,
    )
    print(f"applied; backup: {backup_root}")
    return backup_root


def _replace_candidate_path(source: Path, destination: Path) -> None:
    _remove_path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    _copy_regular_path(source, destination)


def _active_inventory_pairs(home: Path, candidate: Path) -> list[tuple[Path, Path]]:
    return [
        (home / ".codex" / "hooks" / name, candidate / "hooks" / "scripts" / name)
        for name in HOOK_SCRIPT_FILES
    ]


def validate_active_personal_source(skill: Path, home: Path) -> None:
    safe_scoped_path(skill, home, label="active personal skill source")
    validate_regular_path(skill, label="active personal skill source")
    if not skill.is_dir():
        raise RuntimeError(f"active personal skill must be a directory: {skill}")
    for current, directories, files in os.walk(skill, followlinks=False):
        current_path = Path(current)
        for name in directories + files:
            child = current_path / name
            reason = _portable_path_forbidden_reason(child, skill)
            if reason is not None:
                raise RuntimeError(
                    f"forbidden active personal source ({reason}): "
                    f"{child.relative_to(skill).as_posix()}"
                )


def _render_export_candidate(root: Path, home: Path, candidate: Path) -> None:
    shutil.copytree(
        root,
        candidate,
        symlinks=True,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".profile-sync-*")
    )
    active_agents = home / ".codex" / "AGENTS.md"
    safe_scoped_path(active_agents, home, label="active AGENTS source")
    validate_regular_path(active_agents, label="active AGENTS source")
    if not active_agents.is_file():
        raise RuntimeError(f"active AGENTS source must be a file: {active_agents}")
    _replace_candidate_path(active_agents, candidate / "rules" / "AGENTS.portable.md")

    active_skills = home / ".codex" / "skills"
    if path_lexists(active_skills):
        safe_scoped_path(active_skills, home, label="active personal skill root")
        if not active_skills.is_dir():
            raise RuntimeError(f"active personal skill root is not a directory: {active_skills}")
        for skill in sorted(active_skills.iterdir()):
            if not is_portable_codex_skill(skill.name):
                continue
            if skill.name in RETIRED_PERSONAL_SKILLS:
                continue
            validate_active_personal_source(skill, home)
            _replace_candidate_path(
                skill, candidate / "skills" / "codex" / skill.name
            )

    for source, destination in _active_inventory_pairs(home, candidate):
        if not path_lexists(source):
            continue
        safe_scoped_path(source, home, label="active inventory source")
        validate_regular_path(source, label="active inventory source")
        if not source.is_file():
            raise RuntimeError(f"active inventory source must be a file: {source}")
        _replace_candidate_path(source, destination)


def _export_entries(root: Path, candidate: Path) -> list[ManagedEntry]:
    sources = [candidate / "rules" / "AGENTS.portable.md"]
    sources.extend(_personal_skill_directories(candidate))
    sources.extend(candidate / "hooks" / "scripts" / name for name in HOOK_SCRIPT_FILES)
    return [
        ManagedEntry(
            destination=root / source.relative_to(candidate),
            source=source,
            label=source.relative_to(candidate).as_posix(),
        )
        for source in sources
    ]


def export_profile(root: Path, home: Path, *, dry_run: bool) -> list[ManagedEntry]:
    verify_repo(root)
    home = normalized_home(home)
    with tempfile.TemporaryDirectory(prefix=".profile-sync-export-", dir=root.parent) as tmp:
        candidate = Path(tmp) / root.name
        _render_export_candidate(root, home, candidate)
        verify_repo(candidate)
        entries = _export_entries(root, candidate)
        validate_entry_plan(root, entries)
        changed = [entry for entry in entries if not _entry_matches(entry)]
        print(f"outbound managed changes: {len(changed)}")
        for entry in changed:
            print(f"  {entry.label}")
        if dry_run:
            print("dry-run only: repository was not changed")
            return changed

        def post_check() -> None:
            remaining = [entry for entry in changed if not _entry_matches(entry)]
            if remaining:
                raise RuntimeError(f"post-export managed drift remains: {len(remaining)}")

        transactional_replace(changed, base=root, post_check=post_check)
        print("exported portable profile; no Git operation performed")
        return changed


def cmd_audit(args: argparse.Namespace) -> int:
    verify_repo(REPO_ROOT)
    home = normalized_home(Path(args.home))
    _print_inbound(
        inbound_managed_drift(REPO_ROOT, home),
        host_only_personal_skills(REPO_ROOT, home),
    )
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    export_profile(REPO_ROOT, Path(args.home), dry_run=args.dry_run)
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    verify_repo(REPO_ROOT)
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    apply_profile(REPO_ROOT, Path(args.home), confirm=args.confirm)
    return 0


def cmd_push(args: argparse.Namespace) -> int:
    raise SystemExit(
        "legacy sync.py push is disabled and fails closed; use "
        "audit/export, verification, and the authorized Git publication workflow"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", default=str(DEFAULT_HOME), help="active profile home")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("audit").set_defaults(func=cmd_audit)
    export = subparsers.add_parser("export")
    export.add_argument("--dry-run", action="store_true")
    export.set_defaults(func=cmd_export)
    subparsers.add_parser("verify").set_defaults(func=cmd_verify)
    apply = subparsers.add_parser("apply")
    apply.add_argument("--confirm", action="store_true")
    apply.set_defaults(func=cmd_apply)
    push = subparsers.add_parser("push", help="disabled compatibility command")
    push.add_argument("--confirm", action="store_true")
    push.set_defaults(func=cmd_push)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
