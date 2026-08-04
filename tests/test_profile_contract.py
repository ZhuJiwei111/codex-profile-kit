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
        self.assertIn("every substantive continuation turn", planning_prose)
        self.assertIn(
            "one consistency pass across all three files", planning_prose
        )
        self.assertIn("allow_implicit_invocation: true", planning_metadata)

        for contract in (
            "10 minutes or less",
            "explicit request to monitor authorizes one Scheduled registration",
            "fixed local monitoring controller",
            "`gpt-5.6-luna`",
            "`medium` reasoning",
            "one heartbeat automation",
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
            "canonical thread ID",
            "`clientThreadId` is not a canonical task ID",
            "stable schedule ID",
            "`registered_unverified`",
            "Do not wait for the first scheduled run",
            "stops active polling",
            "one bounded fresh sample and exits",
            "directly through `ssh <alias>`",
            "must not relay routine samples through a remote App task",
            "raw-file hash",
            "canonical content self-hash",
            "creation timeouts and interrupted calls are ambiguous",
            "explicitly pre-authorized both actions",
            "exactly matches the current observation contract",
            "created by this registration attempt or discovered as ambiguous during it",
            "never applies to historical, merely similar, or unrelated recurrences",
            "create one isolated live task on the exact target host",
            "stable task ID alone is not enough",
            "live continuation",
            "idle or returns a final answer while the job is still running",
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
            "current-chat",
            "Dynamically select the lowest-cost",
            "with low reasoning",
            "stable thread ID establishes `live_registered`",
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
        self.assertIn("Luna-based read-only monitor", monitor_metadata)
        self.assertIn("fixed gpt-5.6-luna monitoring controller", monitor_metadata)

        for shared_contract in (
            "`registered_unverified`",
            "stable schedule ID",
            "stops active polling",
            "canonical thread ID",
            "idle while the job is still running",
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


if __name__ == "__main__":
    unittest.main()
