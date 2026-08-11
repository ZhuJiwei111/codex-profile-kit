from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time
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
    def test_wiring_contains_owned_guards_and_deferred_stop_hook(self) -> None:
        hooks = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))["hooks"]
        groups = hooks["PreToolUse"]
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
        stop = hooks["Stop"]
        self.assertEqual(len(stop), 1)
        self.assertEqual(len(stop[0]["hooks"]), 1)
        stop_handler = stop[0]["hooks"][0]
        self.assertEqual(stop_handler["timeout"], 3700)
        self.assertEqual(
            stop_handler["command"],
            "{{PROFILE_SYNC_COMMAND:skills/personal-defer-and-resume/scripts/stop_hook.py}}",
        )

    def test_rendered_wiring_uses_absolute_runtime_and_script_paths(self) -> None:
        runtime = Path("/opt/profile python/bin/python")
        codex_home = Path("/Users/example/Codex Home/.codex")
        rendered = json.loads(
            profile_sync.render_hooks(runtime, codex_home).data.decode("utf-8")
        )
        hooks = rendered["hooks"]
        groups = hooks["PreToolUse"] + hooks["Stop"]
        handlers = [
            hook
            for group in groups
            for hook in group["hooks"]
        ]

        self.assertEqual(len(handlers), 3)
        for handler in handlers:
            script_name = Path(shlex.split(handler["command"])[1]).name
            relative = (
                Path("skills/personal-defer-and-resume/scripts/stop_hook.py")
                if script_name == "stop_hook.py"
                else Path("hooks") / script_name
            )
            expected_arguments = [
                str(runtime),
                str(codex_home / relative),
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

    def test_deferred_command_completion_wakes_and_cleans(self) -> None:
        skill = HOOKS.parent / "skills" / "personal-defer-and-resume"
        defer = skill / "scripts" / "defer.py"
        stop_hook = skill / "scripts" / "stop_hook.py"
        with tempfile.TemporaryDirectory() as directory:
            environment = os.environ.copy()
            environment.update(
                {
                    "CODEX_HOME": directory,
                    "CODEX_THREAD_ID": "test-thread",
                    "CODEX_DEFER_POLL_SECONDS": "0.01",
                    "CODEX_DEFER_REARM_SECONDS": "1",
                    "CODEX_DEFER_WAKE_RETRY_SECONDS": "0.05",
                }
            )
            started = subprocess.run(
                [
                    sys.executable,
                    str(defer),
                    "start",
                    "--name",
                    "attention watcher",
                    "--cwd",
                    directory,
                    "--",
                    sys.executable,
                    "-c",
                    "import sys, time; time.sleep(0.05); print('sustained low GPU'); sys.exit(75)",
                ],
                text=True,
                capture_output=True,
                check=True,
                env=environment,
            )
            task_dir = Path(json.loads(started.stdout)["task_dir"])
            metadata = json.loads(
                (task_dir / "metadata.json").read_text(encoding="utf-8")
            )
            self.assertNotIn("command", metadata)

            wake = subprocess.run(
                [sys.executable, str(stop_hook)],
                input="{}",
                text=True,
                capture_output=True,
                check=True,
                env=environment,
                timeout=3,
            )
            wake_value = json.loads(wake.stdout)
            self.assertEqual(wake_value["decision"], "block")
            self.assertIn("exited with code 75", wake_value["reason"])
            self.assertIn(
                "sustained low GPU",
                (task_dir / "output.log").read_text(encoding="utf-8"),
            )

            for action in ("ack", "clean"):
                subprocess.run(
                    [
                        sys.executable,
                        str(defer),
                        action,
                        "--task-dir",
                        str(task_dir),
                    ],
                    text=True,
                    capture_output=True,
                    check=True,
                    env=environment,
                )
            self.assertFalse(task_dir.exists())

    def test_deferred_timeout_records_124(self) -> None:
        defer = (
            HOOKS.parent
            / "skills"
            / "personal-defer-and-resume"
            / "scripts"
            / "defer.py"
        )
        with tempfile.TemporaryDirectory() as directory:
            environment = os.environ.copy()
            environment.update(
                {"CODEX_HOME": directory, "CODEX_THREAD_ID": "test-thread"}
            )
            started = subprocess.run(
                [
                    sys.executable,
                    str(defer),
                    "start",
                    "--name",
                    "timeout",
                    "--cwd",
                    directory,
                    "--timeout",
                    "0.05",
                    "--",
                    sys.executable,
                    "-c",
                    "import time; time.sleep(10)",
                ],
                text=True,
                capture_output=True,
                check=True,
                env=environment,
            )
            task_dir = Path(json.loads(started.stdout)["task_dir"])
            deadline = time.monotonic() + 3
            while (
                not (task_dir / "result.json").exists()
                and time.monotonic() < deadline
            ):
                time.sleep(0.02)
            result = json.loads(
                (task_dir / "result.json").read_text(encoding="utf-8")
            )
            self.assertEqual(result["exit_code"], 124)
            self.assertTrue(result["timed_out"])


if __name__ == "__main__":
    unittest.main()
