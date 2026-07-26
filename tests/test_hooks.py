from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import unittest

from scripts import profile_sync


HOOKS = Path(__file__).resolve().parents[1] / "profile" / "hooks"
HOOKS_JSON = HOOKS.parent / "hooks.json"


def invoke(name: str, tool_name: str, tool_input: dict[str, object]) -> str:
    event = {
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_use_id": "test-call",
    }
    env = os.environ.copy()
    env["CONDA_ROOT"] = "/opt/conda"
    result = subprocess.run(
        [sys.executable, str(HOOKS / name)],
        input=json.dumps(event),
        text=True,
        capture_output=True,
        check=True,
        env=env,
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
            self.assertTrue(
                command.startswith(f"{profile_sync.HOOK_RUNTIME_TOKEN} "),
                command,
            )
            self.assertIn("${CODEX_HOME:-$HOME/.codex}/hooks/", command)

    def test_rendered_wiring_uses_the_sync_interpreter(self) -> None:
        runtime = Path("/opt/profile python/bin/python")
        rendered = json.loads(
            profile_sync.render_hooks(runtime).data.decode("utf-8")
        )
        groups = rendered["hooks"]["PreToolUse"]
        commands = [
            hook["command"]
            for group in groups
            for hook in group["hooks"]
        ]

        self.assertEqual(len(commands), 2)
        for command in commands:
            self.assertEqual(shlex.split(command)[0], str(runtime))
            self.assertNotIn(profile_sync.HOOK_RUNTIME_TOKEN, command)

    def test_conda_guard_denies_only_explicit_base_mutation(self) -> None:
        denied_commands = [
            "conda install demo --name base",
            'conda install demo --name "base"',
            "/opt/conda/bin/conda install demo --name=base",
            "mamba env create -nbase",
            "true && conda create demo --prefix /opt/conda/",
            "true\nconda install demo -p ${CONDA_ROOT}",
            "true # explanation\nconda install demo --name base",
        ]
        allowed_commands = [
            "conda install demo --name project-env",
            "true # conda install demo --name base",
            "echo 'conda install demo --name base'",
            "conda install base --name project-env",
            "conda install demo --name base#suffix",
            "conda list --name base",
        ]

        for command in denied_commands:
            with self.subTest(command=command):
                output = invoke(
                    "conda_base_guard.py",
                    "Bash",
                    {"command": command},
                )
                self.assertEqual(
                    json.loads(output)["hookSpecificOutput"][
                        "permissionDecision"
                    ],
                    "deny",
                )
        for command in allowed_commands:
            with self.subTest(command=command):
                self.assertEqual(
                    invoke(
                        "conda_base_guard.py",
                        "Bash",
                        {"command": command},
                    ),
                    "",
                )

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
