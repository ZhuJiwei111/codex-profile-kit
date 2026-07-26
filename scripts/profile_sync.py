#!/usr/bin/env python3
"""Preview, apply, or check the portable Codex profile."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profile"
MANIFEST = ROOT / "profile-manifest.toml"
PORTABLE_CONFIG = ROOT / "personal.config.toml"
EXEC_BITS = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
CONFIG_KEYS = (
    "model",
    "model_reasoning_effort",
    "plan_mode_reasoning_effort",
    "personality",
    "service_tier",
    "features.memories",
    "memories.generate_memories",
    "memories.use_memories",
    "features.hooks",
    "features.apps",
    "apps._default.enabled",
    "apps._default.approvals_reviewer",
    "apps._default.default_tools_approval_mode",
    "apps.connector_76869538009648d5b282a4bb21c3d157.enabled",
)


class SyncError(RuntimeError):
    pass


@dataclass(frozen=True)
class Leaf:
    data: bytes
    executable: bool


@dataclass(frozen=True)
class Change:
    operation: str
    path: str
    source: Leaf | None
    target: Leaf | None


@dataclass(frozen=True)
class State:
    codex_home: Path
    changes: tuple[Change, ...]
    config_values: dict[str, Any]


def app_server_request(
    codex_home: Path,
    method: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    executable = shutil.which("codex")
    if executable is None:
        raise SyncError("codex executable is unavailable for config/batchWrite")
    environment = os.environ.copy()
    environment["CODEX_HOME"] = str(codex_home)
    try:
        process = subprocess.Popen(
            [executable, "app-server", "--stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=environment,
        )
    except OSError as exc:
        raise SyncError(f"cannot run app-server {method}: {exc}") from exc

    def send(message: dict[str, Any]) -> None:
        if process.stdin is None:
            raise SyncError("app-server stdin is unavailable")
        process.stdin.write(json.dumps(message, separators=(",", ":")) + "\n")
        process.stdin.flush()

    def receive(request_id: int, request_name: str) -> dict[str, Any]:
        if process.stdout is None:
            raise SyncError("app-server stdout is unavailable")
        while True:
            line = process.stdout.readline()
            if not line:
                detail = process.stderr.read().strip() if process.stderr else ""
                raise SyncError(
                    f"app-server closed before responding to {request_name}: {detail}"
                )
            try:
                response = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SyncError(f"app-server returned invalid JSON: {exc}") from exc
            if not isinstance(response, dict) or response.get("id") != request_id:
                continue
            if "error" in response:
                raise SyncError(
                    f"app-server {request_name} failed: {response['error']}"
                )
            result = response.get("result")
            if not isinstance(result, dict):
                raise SyncError(
                    f"app-server {request_name} returned an invalid result"
                )
            return result

    try:
        send(
            {
                "method": "initialize",
                "id": 1,
                "params": {
                    "clientInfo": {
                        "name": "codex_profile_sync",
                        "title": "Codex Profile Sync",
                        "version": "1.0",
                    }
                },
            }
        )
        receive(1, "initialize")
        send({"method": "initialized", "params": {}})
        send({"method": method, "id": 2, "params": params})
        return receive(2, method)
    except (BrokenPipeError, OSError) as exc:
        raise SyncError(f"app-server {method} transport failed: {exc}") from exc
    finally:
        if process.stdin is not None and not process.stdin.closed:
            try:
                process.stdin.close()
            except OSError:
                pass
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def config_user_version(codex_home: Path, config_path: Path) -> str:
    result = app_server_request(
        codex_home, "config/read", {"includeLayers": True}
    )
    layers = result.get("layers")
    if not isinstance(layers, list):
        raise SyncError("config/read did not return configuration layers")
    expected_file = config_path.resolve(strict=False)
    for layer in layers:
        name = layer.get("name") if isinstance(layer, dict) else None
        if not isinstance(name, dict) or name.get("type") != "user":
            continue
        file_value = name.get("file")
        if (
            name.get("profile") in {None, ""}
            and isinstance(file_value, str)
            and Path(file_value).resolve(strict=False) == expected_file
            and isinstance(layer.get("version"), str)
        ):
            return layer["version"]
    raise SyncError(f"config/read did not expose the user layer for {config_path}")


def write_config(
    codex_home: Path,
    config_path: Path,
    edits: list[dict[str, Any]],
    expected_version: str,
) -> str:
    result = app_server_request(
        codex_home,
        "config/batchWrite",
        {
            "edits": edits,
            "expectedVersion": expected_version,
            "filePath": str(config_path),
            "reloadUserConfig": False,
        },
    )
    version = result.get("version")
    file_value = result.get("filePath")
    if not isinstance(version, str) or not isinstance(file_value, str):
        raise SyncError("config/batchWrite returned an invalid response")
    if Path(file_value).resolve(strict=False) != config_path.resolve(strict=False):
        raise SyncError(f"config/batchWrite wrote an unexpected file: {file_value}")
    return version


def resolve_codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    candidate = Path(configured).expanduser() if configured else Path.home() / ".codex"
    if configured and not candidate.is_absolute():
        raise SyncError("CODEX_HOME must be an absolute path")
    if candidate.is_symlink():
        raise SyncError(f"CODEX_HOME must not be a symlink: {candidate}")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise SyncError(f"CODEX_HOME is unavailable: {candidate}: {exc}") from exc
    if not resolved.is_dir() or resolved == Path(resolved.anchor):
        raise SyncError(f"CODEX_HOME must be an existing non-root directory: {resolved}")
    return resolved


def load_toml(path: Path, *, missing_ok: bool = False) -> dict[str, Any]:
    if path.is_symlink():
        raise SyncError(f"refusing symlink: {path}")
    if missing_ok and not path.exists():
        return {}
    try:
        with path.open("rb") as handle:
            value = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise SyncError(f"cannot read TOML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SyncError(f"TOML root must be a table: {path}")
    return value


def normalized_entry(value: object) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        raise SyncError("manifest entries must be non-empty strings")
    path = PurePosixPath(value)
    if path.is_absolute() or value != str(path) or any(part in {"", ".", ".."} for part in path.parts):
        raise SyncError(f"unsafe manifest entry: {value!r}")
    return path


def load_manifest() -> tuple[tuple[PurePosixPath, ...], tuple[PurePosixPath, ...]]:
    raw = load_toml(MANIFEST)
    if set(raw) != {"files", "trees"}:
        raise SyncError("manifest must contain only files and trees")
    if not isinstance(raw["files"], list) or not isinstance(raw["trees"], list):
        raise SyncError("manifest files and trees must be arrays")
    files = tuple(normalized_entry(value) for value in raw["files"])
    trees = tuple(normalized_entry(value) for value in raw["trees"])
    all_entries = files + trees
    if len(set(all_entries)) != len(all_entries):
        raise SyncError("manifest entries must be unique")
    for index, left in enumerate(all_entries):
        for right in all_entries[index + 1 :]:
            if left.parts == right.parts[: len(left.parts)] or right.parts == left.parts[: len(right.parts)]:
                raise SyncError(f"overlapping manifest entries: {left} and {right}")
    return files, trees


def read_leaf(path: Path) -> Leaf | None:
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(metadata.st_mode):
        raise SyncError(f"refusing symlink: {path}")
    if not stat.S_ISREG(metadata.st_mode):
        raise SyncError(f"managed leaf is not a regular file: {path}")
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise SyncError(f"cannot read {path}: {exc}") from exc
    return Leaf(data, bool(metadata.st_mode & EXEC_BITS))


def scan_tree(path: Path, *, required: bool) -> dict[PurePosixPath, Leaf]:
    if path.is_symlink():
        raise SyncError(f"refusing symlink: {path}")
    if not path.exists():
        if required:
            raise SyncError(f"managed source tree is missing: {path}")
        return {}
    if not path.is_dir():
        raise SyncError(f"managed tree is not a regular directory: {path}")

    def walk_error(error: OSError) -> None:
        raise SyncError(f"cannot scan managed tree {path}: {error}") from error

    leaves: dict[PurePosixPath, Leaf] = {}
    for directory, names, filenames in os.walk(
        path, followlinks=False, onerror=walk_error
    ):
        base = Path(directory)
        for name in names:
            child = base / name
            if child.is_symlink():
                raise SyncError(f"refusing symlink: {child}")
        for name in filenames:
            child = base / name
            relative = PurePosixPath(child.relative_to(path).as_posix())
            leaf = read_leaf(child)
            if leaf is None:
                raise SyncError(f"managed leaf disappeared while reading: {child}")
            leaves[relative] = leaf
    return leaves


def validate_parent(parent: Path, root: Path) -> None:
    try:
        relative = parent.relative_to(root)
    except ValueError as exc:
        raise SyncError(f"managed path escapes its root: {parent}") from exc
    current = root
    for part in relative.parts:
        current /= part
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            return
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise SyncError(f"managed parent is not a regular directory: {current}")


def flatten(value: dict[str, Any], prefix: tuple[str, ...] = ()) -> dict[str, Any]:
    leaves: dict[str, Any] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise SyncError("configuration keys must be strings")
        current = prefix + (key,)
        if isinstance(item, dict):
            leaves.update(flatten(item, current))
        else:
            leaves[".".join(current)] = item
    return leaves


def value_at(value: dict[str, Any], key_path: str) -> tuple[bool, Any]:
    current: Any = value
    for key in key_path.split("."):
        if not isinstance(current, dict) or key not in current:
            return False, None
        current = current[key]
    return True, current


def portable_config_values() -> dict[str, Any]:
    values = flatten(load_toml(PORTABLE_CONFIG))
    if set(values) != set(CONFIG_KEYS):
        missing = sorted(set(CONFIG_KEYS) - set(values))
        extra = sorted(set(values) - set(CONFIG_KEYS))
        raise SyncError(f"portable config keys differ from the allowlist; missing={missing}, extra={extra}")
    return {key: values[key] for key in CONFIG_KEYS}


def config_edits(values: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"keyPath": key, "value": values[key], "mergeStrategy": "replace"}
        for key in CONFIG_KEYS
    ]


def restore_config_edits(active: dict[str, Any]) -> list[dict[str, Any]]:
    edits: list[dict[str, Any]] = []
    for key in CONFIG_KEYS:
        present, value = value_at(active, key)
        edits.append(
            {
                "keyPath": key,
                "value": value if present else None,
                "mergeStrategy": "replace",
            }
        )
    return edits


def compare(codex_home: Path) -> State:
    files, trees = load_manifest()
    changes: list[Change] = []
    for relative in files:
        source_path = PROFILE.joinpath(*relative.parts)
        validate_parent(source_path.parent, PROFILE)
        source = read_leaf(source_path)
        if source is None:
            raise SyncError(f"managed source file is missing: {source_path}")
        target_path = codex_home.joinpath(*relative.parts)
        validate_parent(target_path.parent, codex_home)
        target = read_leaf(target_path)
        if target != source:
            operation = "ADD" if target is None else "CHANGE"
            changes.append(Change(operation, str(relative), source, target))
    for relative in trees:
        source_path = PROFILE.joinpath(*relative.parts)
        target_path = codex_home.joinpath(*relative.parts)
        validate_parent(source_path.parent, PROFILE)
        validate_parent(target_path.parent, codex_home)
        source_tree = scan_tree(source_path, required=True)
        target_tree = scan_tree(target_path, required=False)
        for leaf_path in sorted(set(source_tree) | set(target_tree), key=str):
            source = source_tree.get(leaf_path)
            target = target_tree.get(leaf_path)
            if source == target:
                continue
            operation = "ADD" if target is None else "DELETE" if source is None else "CHANGE"
            changes.append(Change(operation, str(relative / leaf_path), source, target))

    expected = portable_config_values()
    active = load_toml(codex_home / "config.toml", missing_ok=True)
    for key, expected_value in expected.items():
        present, actual = value_at(active, key)
        if not present or actual != expected_value:
            changes.append(
                Change("ADD" if not present else "CHANGE", f"config.toml:{key}", None, None)
            )
    return State(codex_home, tuple(changes), expected)


def print_changes(state: State) -> None:
    print(f"CODEX_HOME: {state.codex_home}")
    if not state.changes:
        print("No changes.")
        return
    for change in state.changes:
        print(f"{change.operation} {change.path}")


def validate_hook_runtime() -> None:
    root_value = os.environ.get("CONDA_ROOT")
    if not root_value:
        raise SyncError("CONDA_ROOT is required to resolve the codex-tools hook runtime")
    root = Path(root_value)
    if not root.is_absolute():
        raise SyncError("CONDA_ROOT must be an absolute path")
    interpreter = root / "envs" / "codex-tools" / "bin" / "python"
    if not interpreter.is_file() or not os.access(interpreter, os.X_OK):
        raise SyncError(f"codex-tools hook interpreter is unavailable: {interpreter}")
    try:
        hooks = json.loads((PROFILE / "hooks.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SyncError(f"invalid portable hooks.json: {exc}") from exc
    if not isinstance(hooks, dict):
        raise SyncError("portable hooks.json must contain a JSON object")
    for name in ("conda_base_guard.py", "no_autoresolution_guard.py"):
        path = PROFILE / "hooks" / name
        leaf = read_leaf(path)
        if leaf is None:
            raise SyncError(f"portable hook handler is missing: {path}")
        try:
            compile(leaf.data, str(path), "exec")
        except SyntaxError as exc:
            raise SyncError(f"portable hook handler has invalid syntax: {path}: {exc}") from exc


def ensure_parent(parent: Path, codex_home: Path) -> list[Path]:
    try:
        relative = parent.relative_to(codex_home)
    except ValueError as exc:
        raise SyncError(f"target escapes CODEX_HOME: {parent}") from exc
    created: list[Path] = []
    current = codex_home
    for part in relative.parts:
        current /= part
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            current.mkdir(mode=0o755)
            created.append(current)
            continue
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise SyncError(f"managed parent is not a regular directory: {current}")
    return created


def fsync_directory(path: Path) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_replace(path: Path, leaf: Leaf) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.profile-sync-", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(leaf.data)
            handle.flush()
            os.fsync(handle.fileno())
            os.fchmod(handle.fileno(), 0o755 if leaf.executable else 0o644)
        os.replace(temporary, path)
        fsync_directory(path.parent)
    except Exception:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise


def unlink_leaf(path: Path) -> None:
    path.unlink()
    fsync_directory(path.parent)


def prune_empty(paths: set[Path], codex_home: Path) -> None:
    for path in sorted(paths, key=lambda item: len(item.parts), reverse=True):
        current = path
        while current != codex_home:
            try:
                current.rmdir()
            except (FileNotFoundError, OSError):
                break
            current = current.parent


def write_backup_leaf(path: Path, leaf: Leaf, backup: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    current = path.parent
    while True:
        os.chmod(current, 0o700)
        if current == backup:
            break
        current = current.parent
    with path.open("xb") as handle:
        handle.write(leaf.data)
        handle.flush()
        os.fsync(handle.fileno())
        os.fchmod(handle.fileno(), 0o700 if leaf.executable else 0o600)


def create_backup(
    state: State,
    file_changes: list[Change],
    config_changed: bool,
) -> Path:
    backup_root = Path(f"{state.codex_home}.profile-sync-backups")
    try:
        if backup_root.is_symlink():
            raise SyncError(f"backup root must not be a symlink: {backup_root}")
        backup_root.mkdir(mode=0o700, parents=False, exist_ok=True)
        if not backup_root.is_dir():
            raise SyncError(f"backup root is not a directory: {backup_root}")
        os.chmod(backup_root, 0o700)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        backup = backup_root / timestamp
        backup.mkdir(mode=0o700)
        for change in file_changes:
            if change.target is not None:
                write_backup_leaf(backup / change.path, change.target, backup)
        config_path = state.codex_home / "config.toml"
        if config_changed and config_path.exists():
            leaf = read_leaf(config_path)
            if leaf is None:
                raise SyncError(f"config disappeared before backup: {config_path}")
            write_backup_leaf(backup / "config.toml", leaf, backup)
        return backup
    except OSError as exc:
        raise SyncError(f"cannot create profile backup under {backup_root}: {exc}") from exc


def managed_config_matches(path: Path, expected: dict[str, Any]) -> bool:
    active = load_toml(path, missing_ok=True)
    for key in CONFIG_KEYS:
        present, value = value_at(active, key)
        expected_present, expected_value = value_at(expected, key)
        if present != expected_present or (present and value != expected_value):
            return False
    return True


def rollback_files(
    applied: list[Change],
    codex_home: Path,
    created_dirs: set[Path],
) -> list[str]:
    errors: list[str] = []
    for change in reversed(applied):
        path = codex_home / change.path
        try:
            created_dirs.update(ensure_parent(path.parent, codex_home))
            current = read_leaf(path)
            if current == change.target:
                continue
            if current != change.source:
                raise SyncError(f"external drift prevents restore: {path}")
            if change.target is None:
                unlink_leaf(path)
            else:
                atomic_replace(path, change.target)
            if read_leaf(path) != change.target:
                raise SyncError(f"restore verification failed: {path}")
        except Exception as exc:
            errors.append(f"{change.path}: {exc}")
    prune_empty(created_dirs, codex_home)
    return errors


def apply_profile(state: State) -> Path | None:
    if not state.changes:
        return None
    if compare(state.codex_home) != state:
        raise SyncError("source or target changed after the diff was computed")
    validate_hook_runtime()

    file_changes = [
        change for change in state.changes if not change.path.startswith("config.toml:")
    ]
    config_changed = any(
        change.path.startswith("config.toml:") for change in state.changes
    )
    config_path = state.codex_home / "config.toml"
    active_config = load_toml(config_path, missing_ok=True)
    expected_version: str | None = None
    if config_changed:
        expected_version = config_user_version(state.codex_home, config_path)

    if compare(state.codex_home) != state:
        raise SyncError("source or target changed during apply preflight")
    backup = create_backup(state, file_changes, config_changed)
    applied: list[Change] = []
    created_dirs: set[Path] = set()
    prune_candidates: set[Path] = set()
    new_config_version: str | None = None
    config_attempted = False

    try:
        for change in file_changes:
            path = state.codex_home / change.path
            created_dirs.update(ensure_parent(path.parent, state.codex_home))
            if read_leaf(path) != change.target:
                raise SyncError(f"target changed before replacement: {path}")
            if change.source is None:
                unlink_leaf(path)
                prune_candidates.add(path.parent)
            else:
                atomic_replace(path, change.source)
            applied.append(change)

        if config_changed:
            if expected_version is None:
                raise SyncError("config preflight did not produce an expectedVersion")
            config_attempted = True
            new_config_version = write_config(
                state.codex_home,
                config_path,
                config_edits(state.config_values),
                expected_version,
            )

        post_state = compare(state.codex_home)
        if post_state.changes:
            raise SyncError("post-check found remaining profile drift")
        prune_empty(prune_candidates, state.codex_home)
        return backup
    except Exception as exc:
        rollback_errors: list[str] = []
        if new_config_version is not None:
            try:
                write_config(
                    state.codex_home,
                    config_path,
                    restore_config_edits(active_config),
                    new_config_version,
                )
                if not managed_config_matches(config_path, active_config):
                    raise SyncError("config restore verification failed")
            except Exception as restore_exc:
                rollback_errors.append(f"config.toml: {restore_exc}")
        elif config_attempted and not managed_config_matches(config_path, active_config):
            rollback_errors.append(
                "config.toml changed but config/batchWrite did not return a restore version"
            )
        rollback_errors.extend(rollback_files(applied, state.codex_home, created_dirs))
        message = f"apply failed: {exc}; backup retained at {backup}"
        if rollback_errors:
            message += "; rollback incomplete: " + " | ".join(rollback_errors)
        else:
            message += "; changed targets restored"
        raise SyncError(message) from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("preview", "apply", "check"))
    args = parser.parse_args()
    try:
        state = compare(resolve_codex_home())
        print_changes(state)
        if args.command == "preview":
            return 0
        if args.command == "check":
            return 0 if not state.changes else 1
        backup = apply_profile(state)
        if backup is not None:
            print(f"Backup: {backup}")
        print("Post-check: clean")
        return 0
    except SyncError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
