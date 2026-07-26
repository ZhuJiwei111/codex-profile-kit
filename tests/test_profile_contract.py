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

        self.assertIn(
            "Monitoring is part of that job's launch contract", monitor_prose
        )
        self.assertIn("one successful initial status sample", monitor_prose)
        self.assertIn("allow_implicit_invocation: true", monitor_metadata)
        self.assertIn(
            "returns one successful initial status sample", coordination_prose
        )

        self.assertIn("recommend `/goal` once", agents_prose)
        self.assertIn("Keep related phases in the same task.", agents_prose)
        self.assertIn(
            "Do not create or select a plan implicitly.", agents_prose
        )


if __name__ == "__main__":
    unittest.main()
