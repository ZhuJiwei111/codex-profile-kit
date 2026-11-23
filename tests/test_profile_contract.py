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
            self.assertNotRegex(text, r"(?m)^\s*TODO:|\[TODO\]")

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
            "Finish the installing task before creating the reload-verification task",
            "created while the installing task is still active",
            "not fresh reload evidence",
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

    def test_research_workflow_replaces_planning_package(self) -> None:
        _, trees, _, retired_trees = profile_sync.load_manifest()
        managed = {str(path) for path in trees}
        retired = {str(path) for path in retired_trees}
        for name in ("personal-research-project", "personal-project-journal"):
            self.assertIn(f"skills/{name}", managed)
        old = "skills/personal-planning-with-files-zh"
        self.assertIn(old, retired)
        self.assertNotIn(old, managed)
        self.assertFalse((PROFILE / old).exists())
        agents = (PROFILE / "AGENTS.md").read_text(encoding="utf-8")
        self.assertNotIn("personal-planning-with-files-zh", agents)

    def test_task_archive_is_manual_and_keeps_action_boundaries(self) -> None:
        root = PROFILE / "skills" / "personal-task-archive"
        skill = " ".join((root / "SKILL.md").read_text().split())
        policy = (root / "agents/openai.yaml").read_text()
        self.assertIn("allow_implicit_invocation: false", policy)
        self.assertIn("Manual only.", skill)
        self.assertIn("native archive action only when explicitly authorized", skill)
        self.assertIn("does not stop, cancel", skill)
        self.assertIn("does not modify memory", skill)
        self.assertIn("exact host/ID pairs", skill)

    def test_research_packages_have_resolvable_local_references(self) -> None:
        import re

        for name in ("personal-research-project", "personal-project-journal"):
            root = PROFILE / "skills" / name
            metadata = (root / "agents/openai.yaml").read_text(encoding="utf-8")
            self.assertIn("$" + name, metadata)
            self.assertIn("allow_implicit_invocation: true", metadata)
            for document in root.rglob("*.md"):
                content = document.read_text(encoding="utf-8")
                for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", content):
                    if "://" in target or target.startswith("#"):
                        continue
                    relative = target.split("#", 1)[0]
                    with self.subTest(document=document, target=target):
                        self.assertTrue((document.parent / relative).is_file())


if __name__ == "__main__":
    unittest.main()
