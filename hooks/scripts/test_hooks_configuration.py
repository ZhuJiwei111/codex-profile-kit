#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


SCRIPT_DIR = Path(__file__).resolve().parent
ACTIVE_HOOKS_JSON = SCRIPT_DIR.parent / "hooks.json"
PROFILE_ROOT = SCRIPT_DIR.parents[1]
PROFILE_TEMPLATE = PROFILE_ROOT / "templates" / "hooks.json.template"
PROFILE_RULES = SCRIPT_DIR.parent / "rules"
ACTIVE_RULES = SCRIPT_DIR.parent / "hookify"
RULES_DIR = PROFILE_RULES if PROFILE_RULES.is_dir() else ACTIVE_RULES
sys.path.insert(0, str(SCRIPT_DIR))
import hookify_codex_runner  # noqa: E402


def load_hooks() -> dict[str, object]:
    if ACTIVE_HOOKS_JSON.is_file():
        return json.loads(ACTIVE_HOOKS_JSON.read_text(encoding="utf-8"))
    text = PROFILE_TEMPLATE.read_text(encoding="utf-8")
    rendered = text.replace("{{HOME}}", "/tmp/codex-home").replace(
        "{{PYTHON3}}", "python3"
    )
    return json.loads(rendered)


class HooksConfigurationTest(unittest.TestCase):
    def test_real_unittest_discovery_collects_hook_tests(self) -> None:
        suite = unittest.defaultTestLoader.discover(
            str(SCRIPT_DIR), pattern="test_*.py"
        )

        self.assertGreater(suite.countTestCases(), 0)

    def test_all_controlled_rules_compile_and_have_unique_names(self) -> None:
        rules, diagnostics = hookify_codex_runner.load_rules()

        self.assertEqual(diagnostics, [])
        names = [rule.name for rule in rules]
        self.assertEqual(len(names), len(set(names)))

    def test_only_pre_tool_use_is_registered(self) -> None:
        hooks = load_hooks()["hooks"]

        self.assertEqual(set(hooks), {"PreToolUse"})

    def test_pre_tool_use_uses_canonical_matchers_and_three_handlers(self) -> None:
        groups = load_hooks()["hooks"]["PreToolUse"]
        by_matcher = {group["matcher"]: group["hooks"] for group in groups}

        self.assertEqual(set(by_matcher), {"^Bash$", "^apply_patch$"})
        self.assertEqual(len(by_matcher["^Bash$"]), 2)
        self.assertEqual(len(by_matcher["^apply_patch$"]), 1)
        commands = [
            handler["command"]
            for handlers in by_matcher.values()
            for handler in handlers
        ]
        self.assertEqual(sum("direct_download_guard.py" in value for value in commands), 1)
        self.assertEqual(sum("hookify_codex_runner.py" in value for value in commands), 2)
        self.assertFalse(any("smart_commit" in value for value in commands))

    def test_retired_smart_commit_files_are_absent(self) -> None:
        candidates = [
            SCRIPT_DIR / "smart_commit_stage.py",
            SCRIPT_DIR / "test_smart_commit_stage.py",
            SCRIPT_DIR / "smart-commit.md",
            SCRIPT_DIR.parent / "docs" / "smart-commit.md",
        ]

        self.assertFalse([path for path in candidates if path.exists()])

    def test_retired_semantic_rules_are_absent(self) -> None:
        retired = {
            "warn-gpu-task-without-device-scope.md",
            "warn-long-running-direct-launch.md",
            "warn-long-running-monitoring.md",
            "warn-package-manager-install.md",
            "warn-sensitive-file-edits.md",
            "warn-sensitive-path-command.md",
            "warn-goal-long-job-monitoring.md",
            "warn-my-concern-discussion-mode.md",
            "warn-project-output-explainer-style-on-stop.md",
            "warn-useful-next-steps-on-stop.md",
        }

        self.assertFalse(retired & {path.name for path in RULES_DIR.glob("*.md")})

    def test_rules_only_use_pre_tool_aliases(self) -> None:
        invalid: list[str] = []
        for path in RULES_DIR.glob("*.md"):
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.startswith("event:") and line.split(":", 1)[1].strip() not in {
                    "bash",
                    "file",
                }:
                    invalid.append(f"{path.name}:{line}")

        self.assertEqual(invalid, [])

    def test_production_hook_scripts_never_run_git_add(self) -> None:
        offenders = []
        for path in SCRIPT_DIR.glob("*.py"):
            if path.name.startswith("test_"):
                continue
            text = path.read_text(encoding="utf-8")
            if '"git", "add"' in text or "'git', 'add'" in text:
                offenders.append(path.name)

        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
