from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts import plugin_sync


class FakeCodex:
    def __init__(self) -> None:
        self.marketplaces: list[dict] = []
        self.installed: list[dict] = [
            {
                "pluginId": plugin_sync.LEGACY_PLUGIN_ID,
                "name": plugin_sync.PLUGIN_NAME,
                "marketplaceName": "personal",
                "version": "0.1.0+codex.legacy",
                "installed": True,
                "enabled": True,
                "source": {"source": "local", "path": "/tmp/legacy-plugin"},
            },
            {
                "pluginId": "unrelated@example",
                "name": "unrelated",
                "marketplaceName": "example",
                "version": "1.0.0",
                "installed": True,
                "enabled": True,
                "source": {"source": "local", "path": "/tmp/unrelated"},
            },
        ]
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, codex_home: Path, arguments: list[str]) -> dict:
        del codex_home
        self.calls.append(tuple(arguments))
        if arguments == ["plugin", "marketplace", "list", "--json"]:
            return {"marketplaces": list(self.marketplaces)}
        if arguments == ["plugin", "list", "--json"]:
            return {"installed": list(self.installed), "available": []}
        if arguments[:3] == ["plugin", "marketplace", "add"]:
            self.marketplaces.append(
                {"name": plugin_sync.MARKETPLACE_NAME, "root": str(plugin_sync.ROOT)}
            )
            return {"name": plugin_sync.MARKETPLACE_NAME}
        if arguments[:3] == ["plugin", "add", plugin_sync.PLUGIN_ID]:
            self.installed = [
                item for item in self.installed if item.get("pluginId") != plugin_sync.PLUGIN_ID
            ]
            self.installed.append(
                {
                    "pluginId": plugin_sync.PLUGIN_ID,
                    "name": plugin_sync.PLUGIN_NAME,
                    "marketplaceName": plugin_sync.MARKETPLACE_NAME,
                    "version": plugin_sync.validate_source(),
                    "installed": True,
                    "enabled": True,
                    "source": {
                        "source": "local",
                        "path": str(plugin_sync.PLUGIN_ROOT),
                    },
                }
            )
            return {"pluginId": plugin_sync.PLUGIN_ID}
        if arguments[:3] == ["plugin", "remove", plugin_sync.LEGACY_PLUGIN_ID]:
            self.installed = [
                item
                for item in self.installed
                if item.get("pluginId") != plugin_sync.LEGACY_PLUGIN_ID
            ]
            return {"pluginId": plugin_sync.LEGACY_PLUGIN_ID}
        raise AssertionError(f"unexpected Codex arguments: {arguments}")


class PluginSyncTest(unittest.TestCase):
    def test_direct_cli_imports_sibling_profile_sync(self) -> None:
        result = subprocess.run(
            [sys.executable, str(plugin_sync.ROOT / "scripts" / "plugin_sync.py"), "--help"],
            cwd=plugin_sync.ROOT,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_codex_commands_use_profile_executable_resolver(self) -> None:
        completed = mock.Mock(returncode=0, stdout='{"installed": []}', stderr="")
        with mock.patch.object(
            plugin_sync.profile_sync,
            "resolve_codex_executable",
            return_value="codex-stable",
        ) as resolve, mock.patch.object(
            plugin_sync.subprocess,
            "run",
            return_value=completed,
        ) as run:
            value = plugin_sync.run_codex_json(
                Path("profile-home"), ["plugin", "list", "--json"]
            )

        resolve.assert_called_once_with()
        self.assertEqual(value, {"installed": []})
        self.assertEqual(run.call_args.args[0], ["codex-stable", "plugin", "list", "--json"])
        self.assertEqual(run.call_args.kwargs["encoding"], "utf-8")

    def test_validate_host_runs_process_identity_with_plugin_python(self) -> None:
        completed = mock.Mock(returncode=0, stdout="process identity available", stderr="")
        with mock.patch.object(
            plugin_sync.shutil, "which", return_value="/usr/bin/python3"
        ) as which, mock.patch.object(
            plugin_sync.subprocess, "run", return_value=completed
        ) as run:
            plugin_sync.validate_host()

        which.assert_called_once_with("python3")
        run.assert_called_once_with(
            [
                "/usr/bin/python3",
                str(plugin_sync.PLUGIN_ROOT / "scripts" / "process_identity.py"),
            ],
            text=True,
            capture_output=True,
            check=False,
            timeout=5,
        )

    def test_validate_host_reports_process_identity_probe_failure(self) -> None:
        completed = mock.Mock(returncode=1, stdout="", stderr="ERROR: unsupported")
        with mock.patch.object(
            plugin_sync.shutil, "which", return_value="/usr/bin/python3"
        ), mock.patch.object(
            plugin_sync.subprocess, "run", return_value=completed
        ), self.assertRaisesRegex(plugin_sync.PluginSyncError, "unsupported"):
            plugin_sync.validate_host()

    def test_source_contract_is_portable_and_bounded(self) -> None:
        version = plugin_sync.validate_source()
        self.assertRegex(version, r"^0\.4\.0\+codex\.[A-Za-z0-9._-]+$")

        mcp = plugin_sync.read_json(plugin_sync.PLUGIN_ROOT / ".mcp.json")
        server = mcp["mcpServers"]["long_job_supervisor"]
        self.assertEqual(server["cwd"], ".")
        self.assertEqual(server["command"], "python3")
        self.assertEqual(server["args"], ["./scripts/mcp_server.py"])
        self.assertNotIn("/home/", str(mcp))
        for path in (
            plugin_sync.PLUGIN_ROOT / ".codex-plugin" / "plugin.json",
            plugin_sync.PLUGIN_ROOT / "scripts" / "monitoring.py",
            plugin_sync.PLUGIN_ROOT / "scripts" / "supervisor.py",
            plugin_sync.PLUGIN_ROOT / "skills" / "supervise-long-jobs" / "SKILL.md",
        ):
            self.assertNotIn("systemd", path.read_text(encoding="utf-8").lower())

    def test_preview_reports_marketplace_install_and_exact_legacy_retirement(self) -> None:
        fake = FakeCodex()
        with tempfile.TemporaryDirectory() as directory:
            state = plugin_sync.inspect_state(Path(directory), runner=fake)

        self.assertEqual(
            state.changes,
            (
                plugin_sync.Change("ADD", "marketplace:profile-kit"),
                plugin_sync.Change("ADD", f"plugin:{plugin_sync.PLUGIN_ID}"),
                plugin_sync.Change("DELETE", f"plugin:{plugin_sync.LEGACY_PLUGIN_ID}"),
            ),
        )

    def test_apply_installs_new_plugin_before_removing_only_legacy_selector(self) -> None:
        fake = FakeCodex()
        revision = "a" * 40
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            plugin_sync, "validate_host"
        ), mock.patch.object(
            plugin_sync.profile_sync,
            "git_source_revision",
            return_value=(revision, False),
        ):
            final = plugin_sync.apply_plugins(Path(directory), runner=fake)

        self.assertEqual(final.changes, ())
        add_index = fake.calls.index(("plugin", "add", plugin_sync.PLUGIN_ID, "--json"))
        remove_index = fake.calls.index(
            ("plugin", "remove", plugin_sync.LEGACY_PLUGIN_ID, "--json")
        )
        self.assertLess(add_index, remove_index)
        self.assertTrue(
            any(item.get("pluginId") == "unrelated@example" for item in fake.installed)
        )

    def test_apply_blocks_marketplace_name_collision(self) -> None:
        fake = FakeCodex()
        fake.marketplaces.append(
            {"name": plugin_sync.MARKETPLACE_NAME, "root": "/tmp/other-profile-kit"}
        )
        revision = "b" * 40
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            plugin_sync, "validate_host"
        ), mock.patch.object(
            plugin_sync.profile_sync,
            "git_source_revision",
            return_value=(revision, False),
        ):
            with self.assertRaisesRegex(
                plugin_sync.PluginSyncError, "different root"
            ):
                plugin_sync.apply_plugins(Path(directory), runner=fake)

        self.assertFalse(
            any(call[:3] == ("plugin", "add", plugin_sync.PLUGIN_ID) for call in fake.calls)
        )


if __name__ == "__main__":
    unittest.main()
