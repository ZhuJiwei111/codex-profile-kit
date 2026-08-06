from __future__ import annotations

import re
from pathlib import Path
import tomllib
import unittest

from scripts import profile_sync


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
            self.assertIn(f"${name}", metadata)
            if description.group(1).startswith("Manual only."):
                self.assertIn("allow_implicit_invocation: false", metadata)

    def test_portable_config_has_exact_owned_leaf_keys(self) -> None:
        with (ROOT / "personal.config.toml").open("rb") as handle:
            leaves = profile_sync.flatten(tomllib.load(handle))

        self.assertEqual(set(leaves), set(profile_sync.CONFIG_KEYS))
        self.assertTrue(leaves["features.memories"])
        self.assertFalse(leaves["memories.generate_memories"])
        self.assertTrue(leaves["memories.use_memories"])
        self.assertFalse(leaves["apps._default.enabled"])
        self.assertTrue(
            leaves[
                "apps.connector_76869538009648d5b282a4bb21c3d157.enabled"
            ]
        )

    def test_long_task_continuity_is_sticky_but_opt_in(self) -> None:
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
        monitor = (
            PROFILE
            / "skills"
            / "personal-monitor-external-jobs"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        monitor_metadata = (
            PROFILE
            / "skills"
            / "personal-monitor-external-jobs"
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
        monitor_prose = " ".join(monitor.split())
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

        for contract in (
            "10 minutes or less",
            "explicit request to monitor authorizes one standalone Scheduled registration",
            "standalone Scheduled task",
            "required contract fields that cannot be discovered read-only",
            "exact task identity, status source, terminal evidence, stall evidence",
            "expected remaining duration, and cadence",
            "question card without auto-resolution",
            "proposed cadence",
            "pre-authorization for one live-task fallback",
            "`~/.codex/HOST_LOCAL.md`",
            "as read-only input",
            "never permits creating, editing, or refreshing it",
            "request separate configuration authority",
            "`ssh <alias>`",
            "`ssh -G <alias>`",
            "`BatchMode=yes`",
            "immutable job, run, scheduler identity, or PID plus start time",
            "exact status sources",
            "terminal success/failure evidence",
            "stall evidence",
            "expected remaining-time bucket and proposed sample cadence",
            "stable schedule ID",
            "`registered_unverified`",
            "Do not wait for the first scheduled run",
            "stops active polling",
            "one bounded fresh sample and exits",
            "creation timeouts and interrupted calls are ambiguous",
            "explicitly pre-authorized both actions",
            "exactly matches the current observation contract",
            "created by this registration attempt or discovered as ambiguous during it",
            "never applies to historical, merely similar, or unrelated recurrences",
            "create one isolated live task on the exact target host",
            "`live_registered`",
            "do not wait for its first sample",
            "does not authorize automatic live-task fallback",
            "pause the exact recurrence before reporting",
            "exit without messaging the owner",
            "Queue one event to the owner task",
            "Never interrupt a running owner turn",
            "Do not archive",
            "operating-system sleep suspends observation",
        ):
            self.assertIn(contract, monitor_prose)
        for retired_topology in (
            "Scheduled relay",
            "nonce-bound",
            "controller ledger",
            "next wake",
            "proof run",
            "heartbeat",
            "current-chat",
        ):
            self.assertNotIn(retired_topology, monitor_prose)
        for project_specific in (
            "AIVC",
            "SCI-004",
            "/subing",
            "GSE194122",
            "pretrain",
            "a1001",
        ):
            self.assertNotIn(project_specific, monitor_prose)
        self.assertIn("allow_implicit_invocation: true", monitor_metadata)
        self.assertIn("without blocking the owner", monitor_metadata)
        self.assertIn("register low-cost read-only monitoring", monitor_metadata)

        for shared_contract in (
            "`registered_unverified`",
            "`live_registered`",
            "stable schedule ID",
            "stops active polling",
        ):
            self.assertIn(shared_contract, coordination_prose)
            self.assertIn(shared_contract, agents_prose)
        for obsolete_release_rule in (
            "returns one successful initial status sample",
            "obtain one successful initial sample",
        ):
            self.assertNotIn(obsolete_release_rule, coordination_prose)
            self.assertNotIn(obsolete_release_rule, agents_prose)
            self.assertNotIn(obsolete_release_rule, monitor_prose)

        self.assertIn("recommend `/goal` once", agents_prose)
        self.assertIn("Keep related phases in the same task.", agents_prose)
        self.assertIn(
            "Do not create or select a plan implicitly.", agents_prose
        )

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
        repository_journal = ROOT / ".agent"
        self.assertEqual(
            (repository_journal / "README.md").read_text(encoding="utf-8"),
            readme,
        )
        repository_index = (repository_journal / "JOURNAL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("<!-- journal-months -->", repository_index)
        months = re.findall(
            r"\./journal/(\d{4}-\d{2})\.md", repository_index
        )
        self.assertTrue(months)
        self.assertEqual(months, sorted(set(months), reverse=True))
        for month_name in months:
            month_path = repository_journal / "journal" / f"{month_name}.md"
            self.assertTrue(month_path.is_file(), month_path)
            repository_month = month_path.read_text(encoding="utf-8")
            self.assertIn(
                f"# {month_name} Project Journal", repository_month
            )
            self.assertIn("<!-- journal-entries -->", repository_month)
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
