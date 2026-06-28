#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


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


if __name__ == "__main__":
    unittest.main()
