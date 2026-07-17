#!/usr/bin/env python3
"""Behavior-focused tests for portable profile synchronization."""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import shlex
import shutil
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


sys.dont_write_bytecode = True

SYNC_PATH = Path(__file__).with_name("sync.py")
SPEC = importlib.util.spec_from_file_location("profile_sync", SYNC_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load {SYNC_PATH}")
SYNC = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SYNC
SPEC.loader.exec_module(SYNC)


def write_skill(skill: Path, name: str, marker: str = "v1") -> None:
    (skill / "agents").mkdir(parents=True, exist_ok=True)
    (skill / "references" / "nested").mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        "description: Use for a focused synchronization fixture.\n"
        "---\n\n"
        "Read [the guide](references/guide.md).\n",
        encoding="utf-8",
    )
    (skill / "agents" / "openai.yaml").write_text(
        "interface:\n"
        f"  display_name: \"{name}\"\n"
        "  short_description: \"Focused synchronization fixture\"\n"
        f"  default_prompt: \"Use ${name} for this fixture.\"\n",
        encoding="utf-8",
    )
    (skill / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (skill / "references" / "nested" / "value.txt").write_text(
        marker + "\n", encoding="utf-8"
    )


def make_repo(root: Path, skills: tuple[str, ...] = ("personal-sample",)) -> Path:
    (root / "rules").mkdir(parents=True)
    (root / "templates").mkdir()
    (root / "skills" / "codex").mkdir(parents=True)
    (root / "skills" / "agents").mkdir()
    (root / "agents" / "codex").mkdir(parents=True)
    (root / "hooks" / "rules").mkdir(parents=True)
    (root / "hooks" / "scripts").mkdir()
    (root / "rules" / "AGENTS.portable.md").write_text(
        "# Portable fixture\n", encoding="utf-8"
    )
    (root / "templates" / "config.toml.template").write_text(
        'sandbox_mode = "workspace-write"\n', encoding="utf-8"
    )
    (root / "templates" / "hooks.json.template").write_text(
        '{"command": "{{PYTHON3}} {{HOME}}/.codex/hooks/hookify_codex_runner.py"}\n',
        encoding="utf-8",
    )
    for name in SYNC.CODEX_AGENT_FILES:
        (root / "agents" / "codex" / name).write_text(
            f'name = "{Path(name).stem}"\n', encoding="utf-8"
        )
    for name in SYNC.HOOK_RULE_FILES:
        (root / "hooks" / "rules" / name).write_text(
            f"# {name}\n", encoding="utf-8"
        )
    for name in SYNC.HOOK_SCRIPT_FILES:
        (root / "hooks" / "scripts" / name).write_text(
            f"# {name}\n", encoding="utf-8"
        )
    for name in skills:
        write_skill(root / "skills" / "codex" / name, name)
    return root


def capture(callable_, *args, **kwargs):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        result = callable_(*args, **kwargs)
    return result, output.getvalue()


def backup_directories(home: Path) -> list[Path]:
    archive = home / "codex-migration-archive"
    return sorted(path for path in archive.glob("*") if path.is_dir())


class PersonalOnlyProfileContractTests(unittest.TestCase):
    def test_portable_codex_skill_selection_is_personal_only(self) -> None:
        observed = {
            name: SYNC.is_portable_codex_skill(name)
            for name in (
                "personal-code-simplifier",
                "awesome-rebuttal",
                "find-skills",
            )
        }

        self.assertEqual(
            observed,
            {
                "personal-code-simplifier": True,
                "awesome-rebuttal": False,
                "find-skills": False,
            },
        )

    def test_apply_manages_portable_agents_as_the_active_agents_file(self) -> None:
        home = Path("/tmp/profile-home")

        self.assertIn(
            (
                SYNC.REPO_ROOT / "rules" / "AGENTS.portable.md",
                home / ".codex" / "AGENTS.md",
            ),
            SYNC.apply_pairs(home),
        )

    def test_apply_plan_contains_only_personal_skill_targets(self) -> None:
        home = Path("/tmp/profile-home")
        skill_roots = {
            home / ".codex" / "skills",
            home / ".agents" / "skills",
        }

        non_personal = sorted(
            dst.relative_to(home).as_posix()
            for _, dst in SYNC.apply_pairs(home)
            if dst.parent in skill_roots and not dst.name.startswith("personal-")
        )

        self.assertEqual(non_personal, [])

    def test_confirmed_apply_preserves_target_owned_non_personal_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            sentinels = [
                home / ".codex" / "skills" / "awesome-rebuttal" / "owned.txt",
                home / ".agents" / "skills" / "find-skills" / "owned.txt",
            ]
            for sentinel in sentinels:
                sentinel.parent.mkdir(parents=True)
                sentinel.write_text("target-owned\n", encoding="utf-8")

            args = argparse.Namespace(home=str(home), confirm=True)
            with mock.patch.object(SYNC, "verify_repo"):
                with open(os.devnull, "w", encoding="utf-8") as sink:
                    with mock.patch.object(sys, "stdout", sink):
                        self.assertEqual(SYNC.cmd_apply(args), 0)

            for sentinel in sentinels:
                self.assertEqual(
                    sentinel.read_text(encoding="utf-8"),
                    "target-owned\n",
                )

    def test_repo_verify_rejects_a_non_personal_codex_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "profile"
            skill = root / "skills" / "codex" / "vendor-sample"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: vendor-sample\n"
                "description: Non-personal verification fixture.\n---\n",
                encoding="utf-8",
            )

            with self.assertRaises(SystemExit):
                SYNC.validate_skills(root)


class VerifyContractTests(unittest.TestCase):
    def test_minimal_personal_repo_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp) / "profile")

            _, output = capture(SYNC.verify_repo, root)

            self.assertIn("verification ok", output)

    def test_non_personal_and_agent_skill_content_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp) / "profile")
            vendor = root / "skills" / "codex" / "vendor-sample"
            vendor.mkdir()
            with self.assertRaisesRegex(SystemExit, "non-personal"):
                SYNC.verify_repo(root)
            vendor.rmdir()
            (root / "skills" / "agents" / "find-skills").mkdir()
            with self.assertRaisesRegex(SystemExit, "skills/agents"):
                SYNC.verify_repo(root)

    def test_managed_symlinks_and_sensitive_state_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp) / "profile")
            forbidden = root / "templates" / "auth.json"
            forbidden.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "forbidden"):
                SYNC.verify_repo(root)
            forbidden.unlink()
            outside = root / "outside.txt"
            outside.write_text("outside\n", encoding="utf-8")
            link = root / "skills" / "codex" / "personal-sample" / "linked"
            link.symlink_to(outside)
            with self.assertRaisesRegex(SystemExit, "symbolic link"):
                SYNC.verify_repo(root)

    def test_repo_inventory_is_exact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp) / "profile")
            extra_agent = root / "agents" / "codex" / "extra.toml"
            extra_agent.write_text('name = "extra"\n', encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "inventory mismatch"):
                SYNC.verify_repo(root)
            extra_agent.unlink()
            extra_hook = root / "hooks" / "scripts" / "extra.py"
            extra_hook.write_text("# extra\n", encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "inventory mismatch"):
                SYNC.verify_repo(root)

    def test_relative_skill_resources_must_exist_and_stay_inside_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp) / "profile")
            skill_file = root / "skills" / "codex" / "personal-sample" / "SKILL.md"
            SYNC.verify_repo(root)
            skill_file.write_text(
                skill_file.read_text(encoding="utf-8").replace(
                    "references/guide.md", "references/missing.md"
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(SystemExit, "missing skill resource"):
                SYNC.verify_repo(root)
            (root / "outside.md").write_text("outside\n", encoding="utf-8")
            skill_file.write_text(
                skill_file.read_text(encoding="utf-8").replace(
                    "references/missing.md", "../../../outside.md"
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(SystemExit, "escapes skill"):
                SYNC.verify_repo(root)

    def test_openai_json_and_toml_have_cheap_structural_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp) / "profile")
            yaml = root / "skills" / "codex" / "personal-sample" / "agents" / "openai.yaml"
            yaml.write_text("interface:\n  display_name: sample\n", encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "interface key"):
                SYNC.verify_repo(root)
            write_skill(root / "skills" / "codex" / "personal-sample", "personal-sample")
            agent = root / "agents" / "codex" / "monitor.toml"
            agent.write_text('name = "unterminated\n', encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "invalid TOML"):
                SYNC.verify_repo(root)
            agent.write_text('name = "monitor"\n', encoding="utf-8")
            hooks = root / "templates" / "hooks.json.template"
            hooks.write_text("{broken\n", encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "invalid rendered hooks"):
                SYNC.verify_repo(root)


class ApplyContractTests(unittest.TestCase):
    def test_agents_are_fully_replaced_and_backed_up(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = make_repo(base / "profile")
            home = base / "home"
            active = home / ".codex" / "AGENTS.md"
            active.parent.mkdir(parents=True)
            active.write_text("old agents with host suffix\n", encoding="utf-8")

            backup, _ = capture(SYNC.apply_profile, root, home, confirm=True)

            expected = (root / "rules" / "AGENTS.portable.md").read_bytes()
            self.assertEqual(active.read_bytes(), expected)
            self.assertIsNotNone(backup)
            archived = list(backup.glob(".codex/AGENTS.md"))
            self.assertEqual(len(archived), 1)
            self.assertEqual(
                archived[0].read_text(encoding="utf-8"),
                "old agents with host suffix\n",
            )

    def test_apply_preserves_unmanaged_skills_and_installs_prompt_optimizer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = make_repo(base / "profile", ("personal-prompt-optimizer",))
            home = base / "home"
            home.mkdir()
            sentinels = [
                home / ".codex" / "skills" / "awesome-rebuttal" / "owned.txt",
                home / ".agents" / "skills" / "find-skills" / "owned.txt",
                home / ".codex" / "skills" / "personal-host-only" / "owned.txt",
            ]
            for sentinel in sentinels:
                sentinel.parent.mkdir(parents=True)
                sentinel.write_text("owned\n", encoding="utf-8")

            capture(SYNC.apply_profile, root, home, confirm=True)

            for sentinel in sentinels:
                self.assertEqual(sentinel.read_text(encoding="utf-8"), "owned\n")
            self.assertTrue(
                (home / ".codex" / "skills" / "personal-prompt-optimizer" / "SKILL.md").is_file()
            )

    def test_dry_run_detects_nested_drift_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = make_repo(base / "profile")
            home = base / "home"
            home.mkdir()
            capture(SYNC.apply_profile, root, home, confirm=True)
            source = root / "skills" / "codex" / "personal-sample" / "references" / "nested" / "value.txt"
            active = home / ".codex" / "skills" / "personal-sample" / "references" / "nested" / "value.txt"
            source.write_text("v2\n", encoding="utf-8")
            before_backups = backup_directories(home)

            result, output = capture(SYNC.apply_profile, root, home, confirm=False)

            self.assertIsNone(result)
            self.assertIn("changed managed targets: 1", output)
            self.assertIn("current state", output)
            self.assertIn("recomputes targets", output)
            self.assertNotIn("exactly this plan", output)
            self.assertEqual(active.read_text(encoding="utf-8"), "v1\n")
            self.assertEqual(backup_directories(home), before_backups)

    def test_noop_confirm_creates_no_backup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = make_repo(base / "profile")
            home = base / "home"
            home.mkdir()
            capture(SYNC.apply_profile, root, home, confirm=True)
            before = backup_directories(home)

            backup, output = capture(SYNC.apply_profile, root, home, confirm=True)

            self.assertIsNone(backup)
            self.assertIn("no backup created", output)
            self.assertEqual(backup_directories(home), before)

    def test_target_symlinks_escape_and_source_symlinks_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = make_repo(base / "profile")
            home = base / "home"
            home.mkdir()
            elsewhere = base / "elsewhere"
            elsewhere.mkdir()
            (home / ".codex").symlink_to(elsewhere, target_is_directory=True)
            with self.assertRaisesRegex(RuntimeError, "symbolic-link component"):
                SYNC.apply_profile(root, home, confirm=False)
            with self.assertRaisesRegex(RuntimeError, "escapes managed root"):
                SYNC.validate_entry_plan(
                    home,
                    [
                        SYNC.ManagedEntry(
                            destination=home / "inside" / ".." / ".." / "outside",
                            content=b"x",
                        )
                    ],
                )
            (home / ".codex").unlink()
            outside = base / "outside.txt"
            outside.write_text("outside\n", encoding="utf-8")
            source_link = root / "skills" / "codex" / "personal-sample" / "source-link"
            source_link.symlink_to(outside)
            with self.assertRaisesRegex(SystemExit, "symbolic link"):
                SYNC.apply_profile(root, home, confirm=False)

    def test_cross_target_failure_rolls_back_every_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = make_repo(base / "profile")
            home = base / "home"
            home.mkdir()
            capture(SYNC.apply_profile, root, home, confirm=True)
            active_agents = home / ".codex" / "AGENTS.md"
            active_nested = home / ".codex" / "skills" / "personal-sample" / "references" / "nested" / "value.txt"
            old_agents = active_agents.read_bytes()
            old_nested = active_nested.read_bytes()
            (root / "rules" / "AGENTS.portable.md").write_text("new agents\n", encoding="utf-8")
            (root / "skills" / "codex" / "personal-sample" / "references" / "nested" / "value.txt").write_text(
                "v2\n", encoding="utf-8"
            )
            before_backups = backup_directories(home)
            real_promote = SYNC.promote_staged_path
            calls = 0

            def fail_second(stage: Path, destination: Path) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected promotion failure")
                real_promote(stage, destination)

            with mock.patch.object(SYNC, "promote_staged_path", side_effect=fail_second):
                with self.assertRaisesRegex(OSError, "injected"):
                    capture(SYNC.apply_profile, root, home, confirm=True)

            self.assertEqual(active_agents.read_bytes(), old_agents)
            self.assertEqual(active_nested.read_bytes(), old_nested)
            self.assertEqual(backup_directories(home), before_backups)


class ExportAndAuditContractTests(unittest.TestCase):
    def test_export_replaces_agents_adds_active_personal_and_preserves_repo_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = make_repo(base / "profile", ("personal-repo-only",))
            home = base / "home"
            home.mkdir()
            capture(SYNC.apply_profile, root, home, confirm=True)
            active_agents = home / ".codex" / "AGENTS.md"
            active_agents.write_text("# Full active AGENTS\nHost-specific text.\n", encoding="utf-8")
            write_skill(
                home / ".codex" / "skills" / "personal-prompt-optimizer",
                "personal-prompt-optimizer",
            )
            unmanaged = [
                home / ".codex" / "skills" / "awesome-rebuttal" / "owned.txt",
                home / ".agents" / "skills" / "find-skills" / "owned.txt",
            ]
            for path in unmanaged:
                path.parent.mkdir(parents=True)
                path.write_text("owned\n", encoding="utf-8")
            (home / ".codex" / "agents" / "extra.toml").write_text(
                'name = "extra"\n', encoding="utf-8"
            )
            (home / ".codex" / "hooks" / "extra.py").write_text(
                "# extra\n", encoding="utf-8"
            )
            for name in ("config.toml", "HOST_LOCAL.md", "auth.json"):
                (home / ".codex" / name).write_text("private\n", encoding="utf-8")
            config_before = (root / "templates" / "config.toml.template").read_bytes()

            capture(SYNC.export_profile, root, home, dry_run=False)

            self.assertEqual(
                (root / "rules" / "AGENTS.portable.md").read_bytes(),
                active_agents.read_bytes(),
            )
            self.assertTrue((root / "skills" / "codex" / "personal-repo-only").is_dir())
            self.assertTrue(
                (root / "skills" / "codex" / "personal-prompt-optimizer").is_dir()
            )
            self.assertFalse((root / "skills" / "codex" / "awesome-rebuttal").exists())
            self.assertFalse((root / "agents" / "codex" / "extra.toml").exists())
            self.assertFalse((root / "hooks" / "scripts" / "extra.py").exists())
            self.assertEqual(
                (root / "templates" / "config.toml.template").read_bytes(), config_before
            )
            self.assertFalse((root / "HOST_LOCAL.md").exists())
            self.assertFalse((root / "auth.json").exists())

    def test_export_dry_run_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = make_repo(base / "profile")
            home = base / "home"
            home.mkdir()
            capture(SYNC.apply_profile, root, home, confirm=True)
            active = home / ".codex" / "AGENTS.md"
            active.write_text("changed active agents\n", encoding="utf-8")
            repo_agents = root / "rules" / "AGENTS.portable.md"
            before = repo_agents.read_bytes()

            changes, output = capture(SYNC.export_profile, root, home, dry_run=True)

            self.assertTrue(changes)
            self.assertIn("repository was not changed", output)
            self.assertEqual(repo_agents.read_bytes(), before)

    def test_export_fails_closed_on_non_personal_repo_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = make_repo(base / "profile")
            vendor = root / "skills" / "codex" / "vendor"
            vendor.mkdir()
            home = base / "home"
            home.mkdir()
            with self.assertRaisesRegex(SystemExit, "non-personal"):
                SYNC.export_profile(root, home, dry_run=True)

    def test_audit_separates_drift_and_host_only_personal_additions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = make_repo(base / "profile")
            home = base / "home"
            home.mkdir()
            capture(SYNC.apply_profile, root, home, confirm=True)
            (home / ".codex" / "AGENTS.md").write_text("drift\n", encoding="utf-8")
            (home / ".codex" / "skills" / "personal-host-only").mkdir()
            (home / ".codex" / "skills" / "awesome-rebuttal").mkdir()
            args = argparse.Namespace(home=str(home))

            with mock.patch.object(SYNC, "REPO_ROOT", root):
                _, output = capture(SYNC.cmd_audit, args)

            self.assertIn("inbound managed drift: 1", output)
            self.assertIn("host-only personal additions: 1", output)
            self.assertIn("personal-host-only", output)
            self.assertNotIn("awesome-rebuttal", output)


class AcceptedSecurityContractTests(unittest.TestCase):
    def test_repo_personal_sensitive_paths_are_rejected(self) -> None:
        fixtures = (
            Path(".git/config"),
            Path(".env"),
            Path(".netrc"),
            Path("HOST_LOCAL.md"),
            Path("private-key.PEM"),
        )
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for index, relative in enumerate(fixtures):
                with self.subTest(relative=relative.as_posix()):
                    root = make_repo(base / f"profile-{index}")
                    sensitive = (
                        root / "skills" / "codex" / "personal-sample" / relative
                    )
                    sensitive.parent.mkdir(parents=True, exist_ok=True)
                    sensitive.write_text("private\n", encoding="utf-8")

                    with self.assertRaisesRegex(
                        SystemExit, "forbidden portable path"
                    ):
                        SYNC.verify_repo(root)

    def test_ordinary_auth_and_credential_named_sources_are_portable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = make_repo(base / "profile")
            skill = root / "skills" / "codex" / "personal-sample"
            (skill / "references" / "auth.md").write_text(
                "# Authentication guide\n", encoding="utf-8"
            )
            (skill / "credential_helper.py").write_text(
                "# Public credential helper example\n", encoding="utf-8"
            )
            SYNC.verify_repo(root)
            home = base / "home"
            home.mkdir()
            capture(SYNC.apply_profile, root, home, confirm=True)

            changes, _ = capture(SYNC.export_profile, root, home, dry_run=True)

            self.assertEqual(changes, [])

    def test_source_notes_links_are_ignored_by_routine_verify(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp) / "profile")
            source_notes = (
                root
                / "skills"
                / "codex"
                / "personal-sample"
                / "references"
                / "source-notes.md"
            )
            source_notes.write_text(
                "# Historical source notes\n\n[stale](removed-upstream.md)\n",
                encoding="utf-8",
            )

            _, output = capture(SYNC.verify_repo, root)

            self.assertIn("verification ok", output)

    def test_active_personal_forbidden_sources_fail_before_export_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = make_repo(base / "profile")
            home = base / "home"
            home.mkdir()
            capture(SYNC.apply_profile, root, home, confirm=True)
            active_skill = home / ".codex" / "skills" / "personal-sample"
            repo_skill = root / "skills" / "codex" / "personal-sample"
            real_replace = SYNC._replace_candidate_path
            for relative in (
                Path(".git/config"),
                Path(".env"),
                Path("host_local.Md"),
            ):
                with self.subTest(relative=relative.as_posix()):
                    forbidden = active_skill / relative
                    forbidden.parent.mkdir(parents=True, exist_ok=True)
                    forbidden.write_text("private\n", encoding="utf-8")
                    with mock.patch.object(
                        SYNC, "_replace_candidate_path", wraps=real_replace
                    ) as replace:
                        with self.assertRaisesRegex(
                            RuntimeError, "forbidden active personal source"
                        ):
                            capture(SYNC.export_profile, root, home, dry_run=True)
                    copied_sources = [call.args[0] for call in replace.call_args_list]
                    self.assertNotIn(active_skill, copied_sources)
                    self.assertFalse((repo_skill / relative).exists())
                    forbidden.unlink()
                    if forbidden.parent != active_skill:
                        forbidden.parent.rmdir()

    def test_export_candidate_preserves_unmanaged_top_level_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = make_repo(base / "profile")
            outside = base / "outside.txt"
            outside.write_text("outside target\n", encoding="utf-8")
            outside_link = root / "unmanaged-outside-link"
            dangling_link = root / "unmanaged-dangling-link"
            outside_link.symlink_to(outside)
            dangling_link.symlink_to(base / "missing-target")
            home = base / "home"
            home.mkdir()
            capture(SYNC.apply_profile, root, home, confirm=True)
            real_verify = SYNC.verify_repo
            inspected_candidates: list[Path] = []

            def inspect_candidate(path: Path) -> None:
                real_verify(path)
                if path == root:
                    return
                inspected_candidates.append(path)
                for source in (outside_link, dangling_link):
                    copied = path / source.name
                    self.assertTrue(copied.is_symlink())
                    self.assertEqual(os.readlink(copied), os.readlink(source))

            with mock.patch.object(SYNC, "verify_repo", side_effect=inspect_candidate):
                capture(SYNC.export_profile, root, home, dry_run=True)

            self.assertEqual(len(inspected_candidates), 1)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "requires os.mkfifo")
    def test_special_files_are_rejected_before_hash_or_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp) / "profile")
            skill = root / "skills" / "codex" / "personal-sample"
            fifo = skill / "runtime.fifo"
            os.mkfifo(fifo)

            with self.assertRaisesRegex(RuntimeError, "special file"):
                SYNC.validate_regular_path(skill, label="managed source")
            with self.assertRaisesRegex(SystemExit, "special file"):
                SYNC.verify_repo(root)

    def test_stage_entry_cleans_partial_stage_on_copy_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "source"
            source.mkdir()
            (source / "value.txt").write_text("value\n", encoding="utf-8")
            destination = base / "target"
            entry = SYNC.ManagedEntry(destination=destination, source=source)
            partial_stages: list[Path] = []

            def fail_after_partial_copy(_source: Path, stage: Path) -> None:
                partial_stages.append(stage)
                stage.mkdir()
                (stage / "partial.txt").write_text("partial\n", encoding="utf-8")
                raise OSError("injected partial copy failure")

            with mock.patch.object(
                SYNC, "_copy_regular_path", side_effect=fail_after_partial_copy
            ):
                with self.assertRaisesRegex(OSError, "partial copy"):
                    SYNC._stage_entry(entry)

            self.assertEqual(len(partial_stages), 1)
            self.assertFalse(SYNC.path_lexists(partial_stages[0]))

    def test_rollback_failure_restores_other_targets_and_preserves_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source_root = base / "sources"
            source_root.mkdir()
            source_one = source_root / "one.txt"
            source_two = source_root / "two.txt"
            source_one.write_text("new-one\n", encoding="utf-8")
            source_two.write_text("new-two\n", encoding="utf-8")
            home = base / "home"
            home.mkdir()
            destination_one = home / "one.txt"
            destination_two = home / "two.txt"
            destination_one.write_text("old-one\n", encoding="utf-8")
            destination_two.write_text("old-two\n", encoding="utf-8")
            entries = [
                SYNC.ManagedEntry(destination=destination_one, source=source_one),
                SYNC.ManagedEntry(destination=destination_two, source=source_two),
            ]
            backup_root = (
                home
                / "codex-migration-archive"
                / "20260717T000000-before-profile-kit-apply"
            )
            real_promote = SYNC.promote_staged_path
            real_replace = os.replace
            promotions = 0

            def fail_second_promotion(stage: Path, destination: Path) -> None:
                nonlocal promotions
                promotions += 1
                if promotions == 2:
                    raise OSError("injected second promotion failure")
                real_promote(stage, destination)

            def fail_one_restore(source: Path, destination: Path) -> None:
                if ".rollback-" in Path(source).name and destination == destination_two:
                    raise OSError("injected restore failure")
                real_replace(source, destination)

            error: BaseException | None = None
            with mock.patch.object(
                SYNC, "promote_staged_path", side_effect=fail_second_promotion
            ):
                with mock.patch.object(os, "replace", side_effect=fail_one_restore):
                    try:
                        SYNC.transactional_replace(
                            entries, base=home, backup_root=backup_root
                        )
                    except BaseException as exc:
                        error = exc

            self.assertEqual(destination_one.read_text(encoding="utf-8"), "old-one\n")
            self.assertFalse(destination_two.exists())
            holds = list(home.glob(".two.txt.rollback-*"))
            self.assertEqual(len(holds), 1)
            self.assertEqual(holds[0].read_text(encoding="utf-8"), "old-two\n")
            self.assertTrue((backup_root / "manifest.json").is_file())
            self.assertEqual(type(error).__name__, "RollbackError")
            self.assertIn(str(destination_two), str(error))
            self.assertIn(str(holds[0]), str(error))
            self.assertIsInstance(error.__cause__, OSError)
            self.assertIn("second promotion", str(error.__cause__))
            self.assertNotIn("old-two", str(error))

    def test_apply_backup_permissions_are_private(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "source.txt"
            source.write_text("new\n", encoding="utf-8")
            home = base / "home"
            home.mkdir()
            destination = home / "target.txt"
            destination.write_text("old\n", encoding="utf-8")
            backup_root = home / "codex-migration-archive" / "snapshot"

            previous_umask = os.umask(0o022)
            try:
                SYNC.transactional_replace(
                    [SYNC.ManagedEntry(destination=destination, source=source)],
                    base=home,
                    backup_root=backup_root,
                )
            finally:
                os.umask(previous_umask)

            self.assertEqual(stat.S_IMODE(backup_root.parent.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(backup_root.stat().st_mode), 0o700)
            self.assertEqual(
                stat.S_IMODE((backup_root / "manifest.json").stat().st_mode),
                0o600,
            )

    def test_partial_backup_failure_leaves_no_incomplete_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "source.txt"
            source.write_text("new\n", encoding="utf-8")
            home = base / "home"
            home.mkdir()
            destination = home / "target.txt"
            destination.write_text("old\n", encoding="utf-8")
            backup_root = home / "codex-migration-archive" / "snapshot"
            real_copy = SYNC._copy_regular_path

            def fail_backup_copy(copy_source: Path, copy_destination: Path) -> None:
                if backup_root in copy_destination.parents:
                    copy_destination.parent.mkdir(parents=True, exist_ok=True)
                    copy_destination.write_text("partial\n", encoding="utf-8")
                    raise OSError("injected backup failure")
                real_copy(copy_source, copy_destination)

            with mock.patch.object(
                SYNC, "_copy_regular_path", side_effect=fail_backup_copy
            ):
                with self.assertRaisesRegex(OSError, "backup failure"):
                    SYNC.transactional_replace(
                        [SYNC.ManagedEntry(destination=destination, source=source)],
                        base=home,
                        backup_root=backup_root,
                    )

            self.assertFalse(backup_root.exists())
            self.assertEqual(destination.read_text(encoding="utf-8"), "old\n")

    def test_target_home_must_not_be_filesystem_root(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "filesystem root"):
            SYNC.normalized_home(Path("/"))

    def test_transaction_rechecks_containment_at_each_phase(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "source.txt"
            source.write_text("new\n", encoding="utf-8")
            home = base / "home"
            home.mkdir()
            destination = home / "target.txt"
            destination.write_text("old\n", encoding="utf-8")
            backup_root = home / "codex-migration-archive" / "snapshot"

            with mock.patch.object(
                SYNC, "safe_scoped_path", wraps=SYNC.safe_scoped_path
            ) as safe:
                SYNC.transactional_replace(
                    [SYNC.ManagedEntry(destination=destination, source=source)],
                    base=home,
                    backup_root=backup_root,
                )

            labels = {
                call.kwargs.get("label")
                for call in safe.call_args_list
                if "label" in call.kwargs
            }
            self.assertTrue(
                {
                    "staging destination",
                    "backup source",
                    "backup destination",
                    "hold destination",
                    "promotion destination",
                }.issubset(labels),
                labels,
            )

    def test_rendered_hook_command_quotes_complex_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = make_repo(base / "profile")
            home = base / "home space;semi'\"quote"
            home.mkdir()

            rendered = SYNC._render_hooks(root, home)
            payload = json.loads(rendered)
            argv = shlex.split(payload["command"])

            self.assertEqual(argv[0], "/usr/bin/python3")
            self.assertEqual(
                argv[1],
                str(home / ".codex" / "hooks" / "hookify_codex_runner.py"),
            )


class CliContractTests(unittest.TestCase):
    def test_legacy_push_fails_closed(self) -> None:
        with self.assertRaisesRegex(SystemExit, "disabled and fails closed"):
            SYNC.cmd_push(argparse.Namespace(confirm=True))

    def test_removed_export_tarball_and_push_message_are_rejected(self) -> None:
        parser = SYNC.build_parser()
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["export", "--tarball"])
            with self.assertRaises(SystemExit):
                parser.parse_args(["push", "--message", "legacy"])


if __name__ == "__main__":
    unittest.main()
