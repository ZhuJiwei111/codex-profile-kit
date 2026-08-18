from __future__ import annotations

import re
from pathlib import Path
import tomllib
import unittest

from scripts import plugin_sync, profile_sync


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profile"


class ProfileContractTest(unittest.TestCase):
    def test_manifest_covers_only_real_regular_sources(self) -> None:
        files, trees, retired_files, retired_trees = profile_sync.load_manifest()
        covered: set[Path] = set()
        for relative in files:
            path = PROFILE.joinpath(*relative.parts)
            self.assertTrue(path.is_file(), path)
            self.assertFalse(path.is_symlink(), path)
            covered.add(path)
        for relative in trees:
            path = PROFILE.joinpath(*relative.parts)
            self.assertTrue(path.is_dir(), path)
            self.assertFalse(path.is_symlink(), path)
            for leaf in path.rglob("*"):
                self.assertFalse(leaf.is_symlink(), leaf)
                if leaf.is_file():
                    covered.add(leaf)

        actual = {path for path in PROFILE.rglob("*") if path.is_file()}
        self.assertEqual(actual, covered)
        for relative in retired_files + retired_trees:
            self.assertFalse(PROFILE.joinpath(*relative.parts).exists(), relative)

    def test_skill_metadata_matches_each_manifest_skill(self) -> None:
        _, trees, _, _ = profile_sync.load_manifest()
        for relative in trees:
            skill = PROFILE.joinpath(*relative.parts)
            name = skill.name
            text = (skill / "SKILL.md").read_text(encoding="utf-8")
            frontmatter = text.split("---", 2)[1]
            frontmatter_name = re.search(r"^name: (.+)$", frontmatter, re.MULTILINE)
            description = re.search(
                r"^description: (.+)$", frontmatter, re.MULTILINE
            )
            self.assertIsNotNone(frontmatter_name, skill)
            self.assertIsNotNone(description, skill)
            self.assertEqual(frontmatter_name.group(1), name)
            self.assertNotIn("TODO", text)

            metadata = (skill / "agents" / "openai.yaml").read_text(
                encoding="utf-8"
            )
            self.assertIn("display_name:", metadata)
            self.assertIn("short_description:", metadata)
            if name.startswith("personal-"):
                self.assertIn(f"${name}", metadata)
            if "disable-model-invocation: true" in frontmatter:
                self.assertIn("allow_implicit_invocation: false", metadata)
            if description.group(1).startswith("Manual only."):
                self.assertIn("allow_implicit_invocation: false", metadata)

    def test_profile_sync_reports_material_file_contents(self) -> None:
        profile_sync_skill = (
            PROFILE / "skills" / "personal-profile-sync" / "SKILL.md"
        ).read_text(encoding="utf-8")
        prose = " ".join(profile_sync_skill.split())

        for contract in (
            "orchestrate both the core profile and `scripts/plugin_sync.py` in that single command",
            "personal-long-job-supervisor@profile-kit",
            "personal-long-job-supervisor@personal",
            "Preserve every other marketplace",
            "material contents of the reviewed diff",
            "actual rules, behavior, configuration keys, or managed entries",
            "When `AGENTS.md` changes",
            "When `profile-manifest.toml` changes",
            "Do not replace this content summary with an abstract objective",
            "use enough of them to cover every material change",
        ):
            self.assertIn(contract, prose)

    def test_repository_marketplace_owns_the_long_job_plugin(self) -> None:
        self.assertEqual(plugin_sync.validate_source(), plugin_sync.read_json(
            plugin_sync.PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
        )["version"])
        marketplace = plugin_sync.read_json(plugin_sync.MARKETPLACE_PATH)
        self.assertEqual(marketplace["name"], "profile-kit")
        self.assertEqual(
            [entry["name"] for entry in marketplace["plugins"]],
            ["personal-long-job-supervisor"],
        )

    def test_portable_config_has_exact_owned_leaf_keys(self) -> None:
        with (ROOT / "personal.config.toml").open("rb") as handle:
            leaves = profile_sync.flatten(tomllib.load(handle))

        self.assertEqual(set(leaves), set(profile_sync.CONFIG_KEYS))
        self.assertTrue(leaves["features.memories"])
        self.assertEqual(
            leaves["features.code_mode.direct_only_tool_namespaces"],
            ["mcp__long_job_supervisor"],
        )
        self.assertFalse(leaves["memories.generate_memories"])
        self.assertTrue(leaves["memories.use_memories"])
        self.assertFalse(leaves["apps._default.enabled"])
        self.assertTrue(
            leaves[
                "apps.connector_76869538009648d5b282a4bb21c3d157.enabled"
            ]
        )
        self.assertEqual(
            leaves[
                "apps.connector_76869538009648d5b282a4bb21c3d157.default_tools_approval_mode"
            ],
            "approve",
        )

    def test_file_plan_continuity_is_sticky_but_opt_in(self) -> None:
        planning = (
            PROFILE
            / "skills"
            / "personal-planning-with-files-zh"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        planning_metadata = (
            PROFILE
            / "skills"
            / "personal-planning-with-files-zh"
            / "agents"
            / "openai.yaml"
        ).read_text(encoding="utf-8")
        coordination = (
            PROFILE
            / "skills"
            / "personal-multiline-coordination"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        agents = (PROFILE / "AGENTS.md").read_text(encoding="utf-8")
        planning_prose = " ".join(planning.split())
        coordination_prose = " ".join(coordination.split())
        agents_prose = " ".join(agents.split())

        self.assertIn(
            "Do not create or select a plan implicitly.", planning_prose
        )
        self.assertIn("two compact current-state files", planning_prose)
        self.assertIn("`task_plan.md`: the sole owner", planning_prose)
        self.assertIn("`findings.md`", planning_prose)
        self.assertIn("Do not create a new `progress.md`", planning_prose)
        self.assertIn("optional legacy record", planning_prose)
        self.assertNotIn("read all three files", planning_prose)
        self.assertIn("allow_implicit_invocation: true", planning_metadata)

        self.assertIn("recommend `/goal` once", agents_prose)
        self.assertIn("Keep related phases in the same task.", agents_prose)
        self.assertIn(
            "Do not create or select a plan implicitly.", agents_prose
        )

    def test_task_archive_is_portable_and_current_host_only(self) -> None:
        _, trees, _, retired_trees = profile_sync.load_manifest()
        managed = {str(path) for path in trees}
        retired = {str(path) for path in retired_trees}
        self.assertIn("skills/personal-task-archive", managed)
        self.assertIn("skills/personal-session-memory-hygiene", retired)

        archive_root = PROFILE / "skills" / "personal-task-archive"
        skill = (archive_root / "SKILL.md").read_text(encoding="utf-8")
        inventory = (archive_root / "references" / "session-inventory.md").read_text(
            encoding="utf-8"
        )
        prose = " ".join(skill.split())
        inventory_prose = " ".join(inventory.split())

        for contract in (
            "current execution host",
            "same exact host identity",
            "manage that host from a task executing there",
            "`personal-thread-closeout`",
            "Treat archival as organization",
            "24 hours",
            "15 days",
            "50",
            "pinned",
            "oldest",
        ):
            self.assertIn(contract, prose)
        for contract in (
            "lightweight",
            "explicitly owns",
            "closed failure",
            "actually archived",
            "thread://",
            "Do not copy a summary by default",
            "does not modify memory",
            "override the age windows",
            "finished subAgent",
            "source or parent metadata",
            "result is delivered",
            "does not stop, cancel",
            "raw unarchived main-task and subAgent totals",
            "An unarchived parent does not protect",
            "never label a candidate count as a host total",
        ):
            self.assertIn(contract.lower(), prose.lower())
        self.assertNotIn("decision card", prose.lower())
        for contract in (
            "Windows, macOS, and Linux",
            "Do not install a parser",
            "Never follow rollout/session paths",
            "Do not use an app-wide list or cross-host count",
            "pages to exhaustion",
            "navigation surface",
            "split as unknown",
        ):
            self.assertIn(contract, inventory_prose)
        self.assertNotIn("current Windows host", prose)
        self.assertNotIn("hostId=local", prose)

    def test_default_project_journal_is_implicit_and_separate(self) -> None:
        journal_root = PROFILE / "skills" / "personal-project-journal"
        journal = (journal_root / "SKILL.md").read_text(encoding="utf-8")
        metadata = (journal_root / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        index = (journal_root / "assets" / "journal-index.md").read_text(
            encoding="utf-8"
        )
        readme = (journal_root / "assets" / "journal-readme.md").read_text(
            encoding="utf-8"
        )
        month = (journal_root / "assets" / "journal-month.md").read_text(
            encoding="utf-8"
        )
        planning = (
            PROFILE
            / "skills"
            / "personal-planning-with-files-zh"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        agents = (PROFILE / "AGENTS.md").read_text(encoding="utf-8")
        journal_prose = " ".join(journal.split())
        planning_prose = " ".join(planning.split())
        agents_prose = " ".join(agents.split())

        self.assertIn("allow_implicit_invocation: true", metadata)
        self.assertIn("$personal-project-journal", metadata)
        for contract in (
            "durable project event",
            "Do not initialize a journal during a read-only task",
            "narrow standing write exception",
            "high",
            "medium",
            "routine",
            "Never predict a future commit or push",
            "JOURNAL owns chronological event history",
            "It never authorizes implementation",
        ):
            self.assertIn(contract, journal_prose)
        self.assertIn("<!-- journal-months -->", index)
        self.assertIn("{{YEAR_MONTH}}", index)
        self.assertIn("<!-- journal-entries -->", month)
        self.assertIn("{{YEAR_MONTH}}", month)
        self.assertIn("Completion alone is never a reason", readme)
        gitignore_lines = (ROOT / ".gitignore").read_text(
            encoding="utf-8"
        ).splitlines()
        self.assertIn("/.agent/", gitignore_lines)
        for contract in (
            "Project journaling is the default for durable project events",
            "Initializing a journal still requires",
            "JOURNAL owns human-readable event history",
            "Journal maintenance grants no Git",
        ):
            self.assertIn(contract, agents_prose)
        for contract in (
            "continuing importance",
            "never reduce an important completed outcome mechanically",
            "let JOURNAL own chronological event history",
            "not a competing current-state ledger",
            "owned independently by `personal-project-journal`",
        ):
            self.assertIn(contract, planning_prose)


if __name__ == "__main__":
    unittest.main()
