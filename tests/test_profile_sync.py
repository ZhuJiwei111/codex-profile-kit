from __future__ import annotations

import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts import profile_sync

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "profile_sync.py"


def symlink_or_skip(
    test_case: unittest.TestCase,
    link: Path,
    target: Path,
    *,
    target_is_directory: bool = False,
) -> None:
    try:
        link.symlink_to(target, target_is_directory=target_is_directory)
    except OSError as exc:
        if os.name == "nt" and getattr(exc, "winerror", None) == 1314:
            test_case.skipTest("Windows symbolic-link privilege is unavailable")
        raise


class ProfileSyncCliTest(unittest.TestCase):
    def test_app_server_command_uses_default_stdio_transport(self) -> None:
        self.assertEqual(
            profile_sync.app_server_command("codex"),
            ["codex", "app-server"],
        )

    def test_app_server_command_bootstraps_legacy_default_service_tier(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            codex_home = Path(directory)
            (codex_home / "config.toml").write_text(
                'service_tier = "default"\n',
                encoding="utf-8",
            )

            command = profile_sync.app_server_command("codex", codex_home)

        self.assertEqual(
            command,
            ["codex", "-c", 'service_tier="fast"', "app-server"],
        )

    def test_preview_retires_legacy_default_service_tier(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            codex_home = Path(directory)
            (codex_home / "config.toml").write_text(
                'service_tier = "default"\n'
                + (ROOT / "personal.config.toml").read_text(encoding="utf-8"),
                encoding="utf-8",
            )

            state = profile_sync.compare(codex_home)

        self.assertIn(
            "config.toml:service_tier",
            [change.path for change in state.changes if change.operation == "DELETE"],
        )

    def test_resolve_codex_executable_prefers_windows_local_app(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            local_app_data = Path(directory)
            expected = local_app_data / "OpenAI" / "Codex" / "bin" / "codex.exe"
            expected.parent.mkdir(parents=True)
            expected.write_bytes(b"placeholder")

            with mock.patch.object(profile_sync.os, "name", "nt"), mock.patch.dict(
                profile_sync.os.environ,
                {"LOCALAPPDATA": str(local_app_data)},
                clear=True,
            ), mock.patch.object(
                profile_sync.shutil,
                "which",
                return_value=r"C:\Program Files\WindowsApps\OpenAI.Codex\codex.exe",
            ):
                resolved = profile_sync.resolve_codex_executable()

        self.assertEqual(resolved, str(expected))

    def test_preview_reports_target_and_exact_add(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            codex_home = Path(directory)
            (codex_home / "config.toml").write_text(
                'model_reasoning_effort = "max"\n'
                + (ROOT / "personal.config.toml").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            live_memory = codex_home / "memories" / "MEMORY.md"
            live_memory.parent.mkdir()
            live_memory.write_text("host-local memory\n", encoding="utf-8")
            env = os.environ.copy()
            env["CODEX_HOME"] = str(codex_home)

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "preview", "--profile-only"],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"CODEX_HOME: {codex_home.resolve()}", result.stdout)
        self.assertRegex(
            result.stdout,
            r"Source revision: [0-9a-f]{40}(?: \(dirty\))?",
        )
        self.assertIn(f"Hook runtime: {sys.executable}", result.stdout)
        self.assertIn("ADD AGENTS.md", result.stdout)
        self.assertNotIn("memories/MEMORY.md", result.stdout)
        self.assertNotIn("config.toml:model_reasoning_effort", result.stdout)

    def test_preview_reports_only_explicit_retirements_as_deletes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            codex_home = Path(directory)
            (codex_home / "config.toml").write_bytes(
                (ROOT / "personal.config.toml").read_bytes()
            )
            retired_hook = codex_home / "hooks" / "direct_download_guard.py"
            retired_hook.parent.mkdir()
            retired_hook.write_text("legacy download hook\n", encoding="utf-8")
            retired_safety_hook = codex_home / "hooks" / "local_safety_guard.py"
            retired_safety_hook.write_text(
                "legacy safety hook\n",
                encoding="utf-8",
            )
            retired_skill = (
                codex_home / "skills" / "personal-brainstorms" / "SKILL.md"
            )
            retired_skill.parent.mkdir(parents=True)
            retired_skill.write_text("legacy skill\n", encoding="utf-8")
            preserved = codex_home / "skills" / "personal-host-only" / "SKILL.md"
            preserved.parent.mkdir(parents=True)
            preserved.write_text("host only\n", encoding="utf-8")
            env = os.environ.copy()
            env["CODEX_HOME"] = str(codex_home)

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "preview", "--profile-only"],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "DELETE hooks/direct_download_guard.py",
            result.stdout,
        )
        self.assertIn(
            "DELETE hooks/local_safety_guard.py",
            result.stdout,
        )
        self.assertIn(
            "DELETE skills/personal-brainstorms/SKILL.md",
            result.stdout,
        )
        self.assertNotIn("personal-host-only", result.stdout)

    def test_compare_rejects_symlinked_managed_parent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            codex_home = parent / "codex-home"
            external = parent / "external"
            codex_home.mkdir()
            external.mkdir()
            (codex_home / "config.toml").write_bytes(
                (ROOT / "personal.config.toml").read_bytes()
            )
            symlink_or_skip(
                self,
                codex_home / "skills",
                external,
                target_is_directory=True,
            )

            with self.assertRaisesRegex(profile_sync.SyncError, "managed parent"):
                profile_sync.compare(codex_home)

    def test_scan_tree_does_not_silently_skip_walk_errors(self) -> None:
        def fail_walk(
            path: Path,
            *,
            followlinks: bool,
            onerror: object | None = None,
        ) -> list[object]:
            if not callable(onerror):
                raise AssertionError("scan_tree did not install an error handler")
            onerror(PermissionError("injected scan failure"))
            return []

        with mock.patch.object(profile_sync.os, "walk", side_effect=fail_walk):
            with self.assertRaisesRegex(profile_sync.SyncError, "cannot scan"):
                profile_sync.scan_tree(ROOT / "profile", required=True)

    def test_apply_mirrors_managed_leaves_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            codex_home = parent / "codex-home"
            codex_home.mkdir()
            (codex_home / "config.toml").write_bytes(
                (ROOT / "personal.config.toml").read_bytes()
            )
            extra = codex_home / "skills" / "personal-grilling" / "obsolete.md"
            extra.parent.mkdir(parents=True)
            extra.write_text("retired", encoding="utf-8")
            unmanaged = codex_home / "skills" / "external-skill" / "SKILL.md"
            unmanaged.parent.mkdir(parents=True)
            unmanaged.write_text("keep", encoding="utf-8")
            live_memory = codex_home / "memories" / "MEMORY.md"
            live_memory.parent.mkdir()
            live_memory.write_text("host-local memory\n", encoding="utf-8")
            retired = (
                codex_home / "skills" / "personal-brainstorms" / "SKILL.md"
            )
            retired.parent.mkdir(parents=True)
            retired.write_text("legacy", encoding="utf-8")
            retired_hook = codex_home / "hooks" / "direct_download_guard.py"
            retired_hook.parent.mkdir(parents=True, exist_ok=True)
            retired_hook.write_text("legacy hook", encoding="utf-8")

            with mock.patch.object(profile_sync, "validate_hook_runtime"):
                backup = profile_sync.apply_profile(profile_sync.compare(codex_home))

            self.assertIsNotNone(backup)
            self.assertEqual(
                (codex_home / "AGENTS.md").read_bytes(),
                (ROOT / "profile" / "AGENTS.md").read_bytes(),
            )
            self.assertFalse(extra.exists())
            self.assertEqual(unmanaged.read_text(encoding="utf-8"), "keep")
            self.assertEqual(
                live_memory.read_text(encoding="utf-8"),
                "host-local memory\n",
            )
            self.assertFalse(retired.exists())
            self.assertFalse(retired_hook.exists())
            self.assertEqual(
                (backup / "skills" / "personal-brainstorms" / "SKILL.md").read_text(
                    encoding="utf-8"
                ),
                "legacy",
            )
            self.assertEqual(
                (backup / "hooks" / "direct_download_guard.py").read_text(
                    encoding="utf-8"
                ),
                "legacy hook",
            )
            source_mode = (
                ROOT / "profile" / "hooks" / "conda_base_guard.py"
            ).stat().st_mode
            target_mode = (
                codex_home / "hooks" / "conda_base_guard.py"
            ).stat().st_mode
            if os.name != "nt":
                self.assertEqual(
                    bool(source_mode & stat.S_IXUSR),
                    bool(target_mode & stat.S_IXUSR),
                )
            self.assertEqual(profile_sync.compare(codex_home).changes, ())
            self.assertIsNone(
                profile_sync.apply_profile(profile_sync.compare(codex_home))
            )

    def test_git_source_revision_requires_a_clean_committed_head(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def git(*arguments: str) -> None:
                subprocess.run(
                    ["git", "-C", str(root), *arguments],
                    check=True,
                    text=True,
                    capture_output=True,
                )

            git("init")
            git("config", "user.name", "Profile Sync Test")
            git("config", "user.email", "profile-sync@example.invalid")
            tracked = root / "tracked.txt"
            tracked.write_text("committed\n", encoding="utf-8")
            git("add", "tracked.txt")
            git("commit", "-m", "Initial test commit")

            revision, dirty = profile_sync.git_source_revision(
                root, require_clean=True
            )
            self.assertRegex(revision, r"^[0-9a-f]{40}$")
            self.assertFalse(dirty)

            tracked.write_text("dirty\n", encoding="utf-8")
            with self.assertRaisesRegex(profile_sync.SyncError, "clean Git worktree"):
                profile_sync.git_source_revision(root, require_clean=True)
            self.assertTrue(
                profile_sync.git_source_revision(root, require_clean=False)[1]
            )

    def test_deployment_lock_rejects_a_concurrent_apply(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            codex_home = Path(directory) / "codex-home"
            codex_home.mkdir()
            with profile_sync.deployment_lock(codex_home):
                with self.assertRaisesRegex(
                    profile_sync.SyncError, "another profile deployment"
                ):
                    with profile_sync.deployment_lock(codex_home):
                        self.fail("nested deployment lock unexpectedly succeeded")

    def test_compare_rejects_symlinked_retired_tree(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            codex_home = parent / "codex-home"
            external = parent / "external"
            codex_home.mkdir()
            external.mkdir()
            (codex_home / "config.toml").write_bytes(
                (ROOT / "personal.config.toml").read_bytes()
            )
            retired = codex_home / "skills" / "personal-brainstorms"
            retired.parent.mkdir()
            symlink_or_skip(
                self,
                retired,
                external,
                target_is_directory=True,
            )

            with self.assertRaisesRegex(profile_sync.SyncError, "refusing symlink"):
                profile_sync.compare(codex_home)

    def test_apply_rolls_back_retirement_after_config_write_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            codex_home = Path(directory) / "codex-home"
            shutil.copytree(ROOT / "profile", codex_home)
            config_path = codex_home / "config.toml"
            config_path.write_text('model = "old"\n', encoding="utf-8")
            retired = codex_home / "skills" / "personal-brainstorms" / "SKILL.md"
            retired.parent.mkdir(parents=True)
            retired.write_text("legacy skill\n", encoding="utf-8")

            with mock.patch.object(
                profile_sync, "validate_hook_runtime"
            ), mock.patch.object(
                profile_sync, "config_user_version", return_value="v1"
            ), mock.patch.object(
                profile_sync,
                "write_config",
                side_effect=profile_sync.SyncError("injected config failure"),
            ):
                with self.assertRaisesRegex(
                    profile_sync.SyncError,
                    "changed targets restored",
                ):
                    profile_sync.apply_profile(profile_sync.compare(codex_home))

            self.assertEqual(retired.read_text(encoding="utf-8"), "legacy skill\n")

    def test_apply_rolls_back_leaves_after_replace_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            codex_home = parent / "codex-home"
            codex_home.mkdir()
            shutil.copytree(ROOT / "profile", codex_home, dirs_exist_ok=True)
            (codex_home / "config.toml").write_bytes(
                (ROOT / "personal.config.toml").read_bytes()
            )
            agents = codex_home / "AGENTS.md"
            hooks_definition = codex_home / "hooks.json"
            agents.write_bytes(b"before agents\n")
            hooks_definition.write_bytes(b'{"hooks": {}}\n')
            calls = 0

            def fail_second(path: Path, leaf: profile_sync.Leaf) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected replace failure")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(leaf.data)
                path.chmod(0o755 if leaf.executable else 0o644)

            with mock.patch.object(profile_sync, "validate_hook_runtime"), mock.patch.object(
                profile_sync, "atomic_replace", side_effect=fail_second
            ):
                with self.assertRaises(profile_sync.SyncError):
                    profile_sync.apply_profile(profile_sync.compare(codex_home))

            self.assertGreaterEqual(calls, 3)
            self.assertEqual(agents.read_bytes(), b"before agents\n")
            self.assertEqual(
                hooks_definition.read_bytes(),
                b'{"hooks": {}}\n',
            )

    def test_apply_writes_config_last_through_batch_api(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            codex_home = parent / "codex-home"
            codex_home.mkdir()
            shutil.copytree(ROOT / "profile", codex_home, dirs_exist_ok=True)
            agents = codex_home / "AGENTS.md"
            agents.write_text("old instructions\n", encoding="utf-8")
            config_path = codex_home / "config.toml"
            config_path.write_text('unmanaged = "keep"\nmodel = "old"\n', encoding="utf-8")
            calls: list[tuple[str, object]] = []

            def fake_version(home: Path, path: Path) -> str:
                calls.append(("read", path))
                return "v1"

            def fake_write(
                home: Path,
                path: Path,
                edits: list[dict[str, object]],
                expected_version: str,
            ) -> str:
                if agents.read_bytes() != (ROOT / "profile" / "AGENTS.md").read_bytes():
                    raise AssertionError(
                        "config write ran before ordinary file replacement"
                    )
                calls.append(("write", (edits, expected_version, path)))
                path.write_text(
                    'unmanaged = "keep"\n'
                    + (ROOT / "personal.config.toml").read_text(encoding="utf-8"),
                    encoding="utf-8",
                )
                return "v2"

            with mock.patch.object(profile_sync, "validate_hook_runtime"), mock.patch.object(
                profile_sync, "config_user_version", side_effect=fake_version
            ), mock.patch.object(profile_sync, "write_config", side_effect=fake_write):
                backup = profile_sync.apply_profile(profile_sync.compare(codex_home))

            self.assertIsNotNone(backup)
            self.assertEqual([name for name, _ in calls], ["read", "write"])
            edits, expected_version, written_path = calls[1][1]
            self.assertEqual(expected_version, "v1")
            self.assertEqual(written_path, config_path)
            self.assertEqual(
                {edit["keyPath"] for edit in edits},
                set(profile_sync.CONFIG_KEYS + profile_sync.RETIRED_CONFIG_KEYS),
            )
            self.assertEqual(
                profile_sync.load_toml(config_path)["unmanaged"],
                "keep",
            )
            self.assertEqual(profile_sync.compare(codex_home).changes, ())


if __name__ == "__main__":
    unittest.main()
