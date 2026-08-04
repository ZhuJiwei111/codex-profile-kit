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
        handlers = {
            matcher: matcher_handlers[0]
            for matcher, matcher_handlers in by_matcher.items()
        }
        commands = {
            matcher: handler["command"]
            for matcher, handler in handlers.items()
        }
        windows_commands = {
            matcher: handler["commandWindows"]
            for matcher, handler in handlers.items()
        }
        self.assertEqual(
            commands["^Bash$"],
            "{{PROFILE_SYNC_COMMAND:hooks/conda_base_guard.py}}",
        )
        self.assertEqual(
            windows_commands["^Bash$"],
            "{{PROFILE_SYNC_COMMAND_WINDOWS:hooks/conda_base_guard.py}}",
        )
        self.assertEqual(
            commands["^request_user_input$"],
            "{{PROFILE_SYNC_COMMAND:hooks/no_autoresolution_guard.py}}",
        )
        self.assertEqual(
            windows_commands["^request_user_input$"],
            "{{PROFILE_SYNC_COMMAND_WINDOWS:hooks/no_autoresolution_guard.py}}",
        )

    def test_rendered_wiring_uses_absolute_runtime_and_script_paths(self) -> None:
        runtime = Path("/opt/profile python/bin/python")
        codex_home = Path("/Users/example/Codex Home/.codex")
        rendered = json.loads(
            profile_sync.render_hooks(runtime, codex_home).data.decode("utf-8")
        )
        groups = rendered["hooks"]["PreToolUse"]
        handlers = [
            hook
            for group in groups
            for hook in group["hooks"]
        ]

        self.assertEqual(len(handlers), 2)
        for handler in handlers:
            script_name = Path(shlex.split(handler["command"])[1]).name
            expected_arguments = [
                str(runtime),
                str(codex_home / "hooks" / script_name),
            ]
            self.assertEqual(shlex.split(handler["command"]), expected_arguments)
            self.assertEqual(
                handler["commandWindows"],
                subprocess.list2cmdline(expected_arguments),
            )
            self.assertNotIn("{{PROFILE_SYNC_COMMAND", handler["command"])
            self.assertNotIn(
                "{{PROFILE_SYNC_COMMAND", handler["commandWindows"]
            )

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
