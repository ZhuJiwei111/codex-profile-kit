#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import hookify_codex_runner


SCRIPT = Path(__file__).with_name("hookify_codex_runner.py")


class HookifyCodexRunnerTest(unittest.TestCase):
    def invoke(self, event: dict[str, object]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--event", "PreToolUse"],
            input=json.dumps(event),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    def test_sensitive_file_path_is_blocked_from_file_path_field(self) -> None:
        result = self.invoke(
            {"tool_name": "Edit", "tool_input": {"file_path": "/root/.codex/auth.json"}}
        )

        self.assertIn("permissionDecision", result.stdout)
        self.assertIn("block-sensitive-file-edits", result.stdout)

    def test_sensitive_file_path_is_blocked_from_apply_patch_header(self) -> None:
        result = self.invoke(
            {
                "tool_name": "apply_patch",
                "tool_input": {
                    "patch": (
                        "*** Begin Patch\n"
                        "*** Update File: /root/.codex/auth.json\n"
                        "@@\n"
                        "-{}\n"
                        "+{}\n"
                        "*** End Patch\n"
                    )
                },
            }
        )

        self.assertIn("permissionDecision", result.stdout)
        self.assertIn("block-sensitive-file-edits", result.stdout)

    def test_project_codex_root_only_loads_hookify_named_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_dir = root / ".codex"
            rules_dir = codex_dir / "hookify"
            rules_dir.mkdir(parents=True)
            ignored = codex_dir / "notes.md"
            root_rule = codex_dir / "hookify-extra.md"
            local_rule = codex_dir / "review.local.md"
            nested_rule = rules_dir / "rule.md"
            for path in (ignored, root_rule, local_rule, nested_rule):
                path.write_text("---\nname: test\n---\n", encoding="utf-8")

            loaded = {path.resolve() for path in hookify_codex_runner.rule_files(root)}

            self.assertNotIn(ignored.resolve(), loaded)
            self.assertIn(root_rule.resolve(), loaded)
            self.assertIn(local_rule.resolve(), loaded)
            self.assertIn(nested_rule.resolve(), loaded)


if __name__ == "__main__":
    unittest.main()
