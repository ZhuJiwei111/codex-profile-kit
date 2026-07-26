#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).with_name("no_autoresolution_guard.py")


class NoAutoResolutionGuardTest(unittest.TestCase):
    def payload(
        self,
        tool_input: dict[str, object],
        tool_name: str = "request_user_input",
    ) -> dict[str, object]:
        return {
            "hook_event_name": "PreToolUse",
            "tool_name": tool_name,
            "tool_input": tool_input,
            "tool_use_id": "test-call",
        }

    def invoke(
        self,
        tool_input: dict[str, object],
        tool_name: str = "request_user_input",
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps(self.payload(tool_input, tool_name)),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    def test_denies_auto_resolution_field(self) -> None:
        result = self.invoke(
            {
                "questions": [{"id": "scope", "question": "Choose scope"}],
                "autoResolutionMs": 60000,
            }
        )

        value = json.loads(result.stdout)
        output = value["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "PreToolUse")
        self.assertEqual(output["permissionDecision"], "deny")
        self.assertIn("autoResolutionMs", output["permissionDecisionReason"])

    def test_field_presence_is_denied_even_when_null(self) -> None:
        result = self.invoke({"questions": [], "autoResolutionMs": None})

        self.assertEqual(
            json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

    def test_question_without_auto_resolution_is_silent(self) -> None:
        result = self.invoke(
            {"questions": [{"id": "scope", "question": "Choose scope"}]}
        )

        self.assertEqual(result.stdout, "")

    def test_adjacent_local_function_tool_is_silent(self) -> None:
        result = self.invoke(
            {"autoResolutionMs": 60000},
            tool_name="update_plan",
        )

        self.assertEqual(result.stdout, "")

    def test_invalid_json_is_diagnostic_only(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input="{broken",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        self.assertEqual(result.stdout, "")
        self.assertIn("invalid input JSON", result.stderr)


if __name__ == "__main__":
    unittest.main()
