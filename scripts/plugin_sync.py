#!/usr/bin/env python3
"""Preview, apply, or check the portable profile's owned Codex plugins."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Callable

try:
    from scripts import profile_sync
except ModuleNotFoundError:  # Direct execution from scripts/.
    import profile_sync  # type: ignore[no-redef]


ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_NAME = "profile-kit"
MARKETPLACE_PATH = ROOT / ".agents" / "plugins" / "marketplace.json"
PLUGIN_NAME = "personal-long-job-supervisor"
PLUGIN_ID = f"{PLUGIN_NAME}@{MARKETPLACE_NAME}"
PLUGIN_ROOT = ROOT / "plugins" / PLUGIN_NAME
LEGACY_PLUGIN_ID = f"{PLUGIN_NAME}@personal"


class PluginSyncError(profile_sync.SyncError):
    pass


@dataclass(frozen=True)
class Change:
    operation: str
    item: str


@dataclass(frozen=True)
class PluginState:
    codex_home: Path
    revision: str
    dirty: bool
    version: str
    marketplaces: tuple[dict, ...]
    installed: tuple[dict, ...]
    changes: tuple[Change, ...]


CodexRunner = Callable[[Path, list[str]], dict]


def read_json(path: Path) -> dict:
    if path.is_symlink():
        raise PluginSyncError(f"refusing symlink: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PluginSyncError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PluginSyncError(f"JSON root must be an object: {path}")
    return value


def validate_source() -> str:
    marketplace = read_json(MARKETPLACE_PATH)
    if marketplace.get("name") != MARKETPLACE_NAME:
        raise PluginSyncError(
            f"marketplace name must be {MARKETPLACE_NAME!r}: {MARKETPLACE_PATH}"
        )
    entries = marketplace.get("plugins")
    if not isinstance(entries, list):
        raise PluginSyncError("marketplace plugins must be an array")
    matching = [entry for entry in entries if isinstance(entry, dict) and entry.get("name") == PLUGIN_NAME]
    if len(matching) != 1:
        raise PluginSyncError(f"marketplace must contain exactly one {PLUGIN_NAME} entry")
    source = matching[0].get("source")
    if source != {"source": "local", "path": f"./plugins/{PLUGIN_NAME}"}:
        raise PluginSyncError(f"unexpected marketplace source for {PLUGIN_NAME}")

    manifest = read_json(PLUGIN_ROOT / ".codex-plugin" / "plugin.json")
    if manifest.get("name") != PLUGIN_NAME:
        raise PluginSyncError("plugin manifest name does not match its directory")
    version = manifest.get("version")
    if not isinstance(version, str) or "+codex." not in version:
        raise PluginSyncError("plugin version must contain one Codex cachebuster")
    if manifest.get("mcpServers") != "./.mcp.json":
        raise PluginSyncError("plugin manifest must point at ./.mcp.json")

    mcp = read_json(PLUGIN_ROOT / ".mcp.json")
    servers = mcp.get("mcpServers")
    server = servers.get("long_job_supervisor") if isinstance(servers, dict) else None
    if not isinstance(server, dict):
        raise PluginSyncError("long_job_supervisor MCP definition is missing")
    if server.get("cwd") != "." or server.get("command") != "python3":
        raise PluginSyncError("MCP server must resolve from the installed plugin root")
    if server.get("args") != ["./scripts/mcp_server.py"]:
        raise PluginSyncError("MCP server path must be plugin-relative")
    if server.get("tool_timeout_sec") != 604800:
        raise PluginSyncError("MCP wait timeout must remain seven days")

    for script in ("mcp_server.py", "supervisor.py", "worker.py"):
        path = PLUGIN_ROOT / "scripts" / script
        try:
            compile(path.read_bytes(), str(path), "exec")
        except (OSError, SyntaxError) as exc:
            raise PluginSyncError(f"invalid plugin script {path}: {exc}") from exc
    return version


def run_codex_json(codex_home: Path, arguments: list[str]) -> dict:
    executable = shutil.which("codex")
    if executable is None:
        raise PluginSyncError("codex executable is unavailable")
    environment = os.environ.copy()
    environment["CODEX_HOME"] = str(codex_home)
    completed = subprocess.run(
        [executable, *arguments],
        text=True,
        capture_output=True,
        check=False,
        env=environment,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()[:2000]
        raise PluginSyncError(
            f"codex {' '.join(arguments)} failed ({completed.returncode}): {detail}"
        )
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise PluginSyncError(
            f"codex {' '.join(arguments)} returned invalid JSON: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise PluginSyncError("Codex plugin command returned a non-object JSON value")
    return value


def inspect_state(
    codex_home: Path,
    *,
    runner: CodexRunner = run_codex_json,
    require_clean: bool = False,
) -> PluginState:
    version = validate_source()
    revision, dirty = profile_sync.git_source_revision(ROOT, require_clean=require_clean)
    marketplace_value = runner(
        codex_home, ["plugin", "marketplace", "list", "--json"]
    )
    plugin_value = runner(codex_home, ["plugin", "list", "--json"])
    marketplaces = marketplace_value.get("marketplaces")
    installed = plugin_value.get("installed")
    if not isinstance(marketplaces, list) or not all(isinstance(item, dict) for item in marketplaces):
        raise PluginSyncError("Codex returned invalid marketplace state")
    if not isinstance(installed, list) or not all(isinstance(item, dict) for item in installed):
        raise PluginSyncError("Codex returned invalid installed-plugin state")

    changes: list[Change] = []
    registered = [item for item in marketplaces if item.get("name") == MARKETPLACE_NAME]
    if not registered:
        changes.append(Change("ADD", f"marketplace:{MARKETPLACE_NAME}"))
    elif len(registered) != 1:
        changes.append(Change("CHANGE", f"marketplace:{MARKETPLACE_NAME}"))
    else:
        root = registered[0].get("root")
        if not isinstance(root, str) or Path(root).resolve(strict=False) != ROOT.resolve(strict=True):
            changes.append(Change("CHANGE", f"marketplace:{MARKETPLACE_NAME}"))

    by_id = {item.get("pluginId"): item for item in installed if isinstance(item.get("pluginId"), str)}
    plugin = by_id.get(PLUGIN_ID)
    if plugin is None:
        changes.append(Change("ADD", f"plugin:{PLUGIN_ID}"))
    else:
        source = plugin.get("source")
        source_path = source.get("path") if isinstance(source, dict) else None
        if (
            plugin.get("version") != version
            or plugin.get("enabled") is not True
            or not isinstance(source_path, str)
            or Path(source_path).resolve(strict=False) != PLUGIN_ROOT.resolve(strict=True)
        ):
            changes.append(Change("CHANGE", f"plugin:{PLUGIN_ID}"))
    if LEGACY_PLUGIN_ID in by_id:
        changes.append(Change("DELETE", f"plugin:{LEGACY_PLUGIN_ID}"))

    return PluginState(
        codex_home=codex_home,
        revision=revision,
        dirty=dirty,
        version=version,
        marketplaces=tuple(marketplaces),
        installed=tuple(installed),
        changes=tuple(changes),
    )


def validate_host() -> None:
    if os.name != "posix" or not sys.platform.startswith("linux"):
        raise PluginSyncError("personal-long-job-supervisor requires Linux systemd --user")
    for executable in ("python3", "systemd-run", "systemctl"):
        if shutil.which(executable) is None:
            raise PluginSyncError(f"required host executable is unavailable: {executable}")
    completed = subprocess.run(
        ["systemctl", "--user", "show-environment"],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()[:1000]
        raise PluginSyncError(f"systemd --user is unavailable: {detail}")


def print_state(state: PluginState) -> None:
    print(f"CODEX_HOME: {state.codex_home}")
    print(f"Source revision: {state.revision}{' (dirty)' if state.dirty else ''}")
    print(f"Marketplace root: {ROOT}")
    print(f"Plugin version: {state.version}")
    if not state.changes:
        print("No plugin changes.")
        return
    for change in state.changes:
        print(f"{change.operation} {change.item}")


def apply_plugins(
    codex_home: Path,
    *,
    runner: CodexRunner = run_codex_json,
) -> PluginState:
    validate_host()
    expected_revision, _ = profile_sync.git_source_revision(ROOT, require_clean=True)
    with profile_sync.deployment_lock(codex_home):
        state = inspect_state(codex_home, runner=runner, require_clean=True)
        if state.revision != expected_revision:
            raise PluginSyncError("plugin source revision changed during apply preflight")
        marketplace_change = next(
            (change for change in state.changes if change.item == f"marketplace:{MARKETPLACE_NAME}"),
            None,
        )
        if marketplace_change is not None:
            if marketplace_change.operation != "ADD":
                raise PluginSyncError(
                    f"marketplace {MARKETPLACE_NAME!r} is already registered at a different root"
                )
            runner(
                codex_home,
                ["plugin", "marketplace", "add", str(ROOT), "--json"],
            )

        state = inspect_state(codex_home, runner=runner, require_clean=True)
        plugin_change = next(
            (change for change in state.changes if change.item == f"plugin:{PLUGIN_ID}"),
            None,
        )
        if plugin_change is not None:
            runner(codex_home, ["plugin", "add", PLUGIN_ID, "--json"])

        state = inspect_state(codex_home, runner=runner, require_clean=True)
        if any(change.item == f"plugin:{PLUGIN_ID}" for change in state.changes):
            raise PluginSyncError("new plugin did not verify; retired selector was preserved")
        if any(change.item == f"plugin:{LEGACY_PLUGIN_ID}" for change in state.changes):
            runner(codex_home, ["plugin", "remove", LEGACY_PLUGIN_ID, "--json"])

        final_state = inspect_state(codex_home, runner=runner, require_clean=True)
        if final_state.revision != expected_revision:
            raise PluginSyncError("plugin source revision changed during apply")
        if final_state.changes:
            raise PluginSyncError("plugin post-check still reports managed drift")
        return final_state


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("preview", "apply", "check"))
    args = parser.parse_args()
    try:
        codex_home = profile_sync.resolve_codex_home()
        state = inspect_state(
            codex_home,
            require_clean=args.command == "apply",
        )
        print_state(state)
        if args.command == "preview":
            return 0
        if args.command == "check":
            return 0 if not state.changes else 1
        final_state = apply_plugins(codex_home)
        print(f"Installed plugin: {PLUGIN_ID}@{final_state.version}")
        print("Plugin post-check: clean")
        return 0
    except (PluginSyncError, profile_sync.SyncError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
