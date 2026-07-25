from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


HOOKS = Path(__file__).resolve().parents[1] / "profile" / "hooks"
HOOKS_JSON = HOOKS.parent / "hooks.json"


def invoke(name: str, tool_name: str, tool_input: dict[str, object]) -> str:
    event = {
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_use_id": "test-call",
    }
    result = subprocess.run(
        [sys.executable, str(HOOKS / name)],
        input=json.dumps(event),
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


class HookBehaviorTest(unittest.TestCase):
    def test_wiring_contains_only_the_two_owned_guards(self) -> None:
        groups = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))["hooks"][
            "PreToolUse"
        ]
        by_matcher = {group["matcher"]: group["hooks"] for group in groups}

        self.assertEqual(set(by_matcher), {"^Bash$", "^request_user_input$"})
        self.assertEqual(len(by_matcher["^Bash$"]), 1)
        self.assertEqual(len(by_matcher["^request_user_input$"]), 1)
        commands = {
            matcher: handlers[0]["command"]
            for matcher, handlers in by_matcher.items()
        }
        self.assertIn("conda_base_guard.py", commands["^Bash$"])
        self.assertIn(
            "no_autoresolution_guard.py",
            commands["^request_user_input$"],
        )
        for command in commands.values():
            self.assertIn("${CONDA_ROOT:?}/envs/codex-tools/bin/python", command)
            self.assertIn("${CODEX_HOME:-$HOME/.codex}/hooks/", command)

    def test_conda_guard_denies_only_explicit_base_mutation(self) -> None:
        denied = invoke(
            "conda_base_guard.py",
            "Bash",
            {"command": "conda install demo --name base"},
        )
        allowed = invoke(
            "conda_base_guard.py",
            "Bash",
            {"command": "conda install demo --name project-env"},
        )

        self.assertEqual(
            json.loads(denied)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )
        self.assertEqual(allowed, "")

    def test_no_autoresolution_guard_checks_field_presence(self) -> None:
        denied = invoke(
            "no_autoresolution_guard.py",
            "request_user_input",
            {"questions": [], "autoResolutionMs": None},
        )
        allowed = invoke(
            "no_autoresolution_guard.py",
            "request_user_input",
            {"questions": []},
        )

        self.assertEqual(
            json.loads(denied)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )
        self.assertEqual(allowed, "")

    def test_adjacent_tools_are_silent(self) -> None:
        self.assertEqual(
            invoke(
                "conda_base_guard.py",
                "apply_patch",
                {"command": "conda install demo --name base"},
            ),
            "",
        )
        self.assertEqual(
            invoke(
                "no_autoresolution_guard.py",
                "update_plan",
                {"autoResolutionMs": 60000},
            ),
            "",
        )


if __name__ == "__main__":
    unittest.main()
