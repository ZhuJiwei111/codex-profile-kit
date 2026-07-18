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
sys.path.insert(0, str(SCRIPT_DIR))


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
        self.assertEqual(sum("local_safety_guard.py" in value for value in commands), 2)
        self.assertFalse(any("smart_commit" in value for value in commands))

    def test_retired_smart_commit_files_are_absent(self) -> None:
        candidates = [
            SCRIPT_DIR / "smart_commit_stage.py",
            SCRIPT_DIR / "test_smart_commit_stage.py",
            SCRIPT_DIR / "smart-commit.md",
            SCRIPT_DIR.parent / "docs" / "smart-commit.md",
        ]

        self.assertFalse([path for path in candidates if path.exists()])

    def test_markdown_adapter_is_fully_retired(self) -> None:
        retired = [
            SCRIPT_DIR / "hookify_codex_runner.py",
            SCRIPT_DIR / "test_hookify_codex_runner.py",
            PROFILE_ROOT / "hooks" / "rules",
        ]

        self.assertFalse([path for path in retired if path.exists()])

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
