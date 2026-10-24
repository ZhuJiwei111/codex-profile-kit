from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

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
    def test_conda_guard_denies_windows_executable_names(self) -> None:
        commands = [
            "conda.exe install demo --name base",
            "conda.bat create --name base",
            "mamba.exe env create -nbase",
            r"& 'C:\Program Files\Conda\Scripts\conda.exe' install demo -n base",
        ]
        if os.name == "nt":
            commands.append(r"D:\Anaconda\Scripts\conda.exe install demo -n base")
        for command in commands:
            with self.subTest(command=command):
                output = invoke("conda_base_guard.py", "Bash", {"command": command})
                self.assertTrue(output, command)
                self.assertEqual(
                    json.loads(output)["hookSpecificOutput"]["permissionDecision"],
                    "deny",
                )

    def test_conda_guard_resolves_base_without_conda_root(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "conda_guard", HOOKS / "conda_base_guard.py"
        )
        guard = importlib.util.module_from_spec(spec)
        with mock.patch.object(sys, "dont_write_bytecode", True):
            spec.loader.exec_module(guard)
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory) / "conda"
            (base / "conda-meta").mkdir(parents=True)
            (base / "condabin").mkdir()
            tools = base / "envs" / "codex-tools"
            unrelated_python = Path(directory) / "python"
            sources = [
                (tools, ""),
                (unrelated_python, str(base / "Scripts" / "conda.exe")),
            ]
            for prefix, executable in sources:
                with self.subTest(prefix=prefix, executable=executable):
                    with mock.patch.dict(
                        os.environ, {"CONDA_ROOT": "", "CONDA_EXE": executable}
                    ), mock.patch.object(guard.sys, "prefix", str(prefix)):
                        self.assertTrue(guard.targets_base(
                            f"conda install demo --prefix '{base}'"
                        ))
                        self.assertFalse(guard.targets_base(
                            f"conda install demo --prefix '{tools}'"
                        ))

    def test_wiring_contains_only_owned_guards(self) -> None:
        hooks = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))["hooks"]
        self.assertEqual(set(hooks), {"PreToolUse"})
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
    def test_rendered_wiring_uses_absolute_runtime_and_script_paths(self) -> None:
        runtime = Path("/opt/profile python/bin/python")
        codex_home = Path("/Users/example/Codex Home/.codex")
        rendered = json.loads(
            profile_sync.render_hooks(runtime, codex_home).data.decode("utf-8")
        )
        hooks = rendered["hooks"]
        groups = hooks["PreToolUse"]
        handlers = [
            hook
            for group in groups
            for hook in group["hooks"]
        ]

        self.assertEqual(len(handlers), 2)
        for handler in handlers:
            script_name = Path(shlex.split(handler["command"])[1]).name
            relative = Path("hooks") / script_name
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
            "conda.exe install demo --name project-env",
            "conda.bat list --name base",
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
