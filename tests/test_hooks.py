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


def deferred_paths() -> tuple[Path, Path]:
    skill = HOOKS.parent / "skills" / "personal-defer-and-resume"
    return skill / "scripts" / "defer.py", skill / "scripts" / "stop_hook.py"


def deferred_environment(directory: str) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(
        {
            "CODEX_HOME": directory,
            "CODEX_THREAD_ID": "test-thread",
            "CODEX_DEFER_POLL_SECONDS": "0.01",
            "CODEX_DEFER_WAKE_RETRY_SECONDS": "0.02",
        }
    )
    return environment


def start_deferred(
    defer: Path,
    directory: str,
    environment: dict[str, str],
    code: str,
    *,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(defer),
            "start",
            "--name",
            "test command",
            "--cwd",
            directory,
            "--",
            sys.executable,
            "-c",
            code,
        ],
        text=True,
        capture_output=True,
        check=check,
        env=environment,
    )


def wait_for_result(task_dir: Path) -> None:
    deadline = time.monotonic() + 3
    while not (task_dir / "result.json").exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    if not (task_dir / "result.json").exists():
        raise AssertionError(f"deferred result was not written: {task_dir}")


def invoke_stop(stop_hook: Path, environment: dict[str, str]) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, str(stop_hook)],
        input="{}",
        text=True,
        capture_output=True,
        check=True,
        env=environment,
        timeout=3,
    )
    return json.loads(completed.stdout)


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

    def test_deferred_missing_worker_records_125(self) -> None:
        defer, _ = deferred_paths()
        with tempfile.TemporaryDirectory() as directory:
            environment = deferred_environment(directory)
            task_dir = (
                Path(directory)
                / "runtime/personal-defer-and-resume/test-thread/stale-task"
            )
            task_dir.mkdir(parents=True)
            (task_dir / "metadata.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "task_id": "stale-task",
                        "thread_id": "test-thread",
                        "name": "stale worker",
                        "cwd": directory,
                        "registered_at": "2000-01-01T00:00:00+00:00",
                    }
                ),
                encoding="utf-8",
            )
            (task_dir / "worker.json").write_text(
                json.dumps(
                    {
                        "pid": 999999,
                        "started_at": "2000-01-01T00:00:00+00:00",
                    }
                ),
                encoding="utf-8",
            )

            status = subprocess.run(
                [sys.executable, str(defer), "status", "--task-dir", str(task_dir)],
                text=True,
                capture_output=True,
                check=True,
                env=environment,
            )
            status_value = json.loads(status.stdout)

            self.assertEqual(status_value["state"], "completed-unacknowledged")
            self.assertEqual(status_value["exit_code"], 125)

    def test_deferred_resume_acknowledges_without_returning_log_output(self) -> None:
        defer, _ = deferred_paths()
        with tempfile.TemporaryDirectory() as directory:
            environment = deferred_environment(directory)
            started = start_deferred(
                defer,
                directory,
                environment,
                "import sys; print('private log'); sys.exit(1)",
            )
            task_dir = Path(json.loads(started.stdout)["task_dir"])
            wait_for_result(task_dir)

            status = subprocess.run(
                [sys.executable, str(defer), "status", "--task-dir", str(task_dir)],
                text=True,
                capture_output=True,
                check=True,
                env=environment,
            )
            self.assertEqual(
                json.loads(status.stdout)["state"],
                "completed-unacknowledged",
            )
            resumed = subprocess.run(
                [sys.executable, str(defer), "resume", "--task-dir", str(task_dir)],
                text=True,
                capture_output=True,
                check=True,
                env=environment,
            )
            resume_value = json.loads(resumed.stdout)

            self.assertEqual(resume_value["status"]["state"], "acknowledged")
            self.assertIn("ack", resume_value)
            self.assertNotIn("output", resume_value)
            self.assertNotIn("output_tail", resume_value)
            self.assertTrue((task_dir / "ack.json").is_file())

    def test_deferred_start_rejects_pending_until_resume(self) -> None:
        defer, _ = deferred_paths()
        with tempfile.TemporaryDirectory() as directory:
            environment = deferred_environment(directory)
            started = start_deferred(
                defer,
                directory,
                environment,
                "import time; time.sleep(0.1)",
            )
            task_dir = Path(json.loads(started.stdout)["task_dir"])

            while_running = start_deferred(
                defer,
                directory,
                environment,
                "pass",
                check=False,
            )
            self.assertNotEqual(while_running.returncode, 0)
            self.assertIn("unacknowledged registration", while_running.stderr)

            wait_for_result(task_dir)
            while_completed = start_deferred(
                defer,
                directory,
                environment,
                "pass",
                check=False,
            )
            self.assertNotEqual(while_completed.returncode, 0)
            self.assertIn("unacknowledged registration", while_completed.stderr)

            subprocess.run(
                [sys.executable, str(defer), "resume", "--task-dir", str(task_dir)],
                text=True,
                capture_output=True,
                check=True,
                env=environment,
            )
            allowed = start_deferred(
                defer,
                directory,
                environment,
                "pass",
            )
            self.assertEqual(allowed.returncode, 0)
            wait_for_result(Path(json.loads(allowed.stdout)["task_dir"]))

    def test_deferred_completion_retries_three_times_then_releases(self) -> None:
        defer, stop_hook = deferred_paths()
        with tempfile.TemporaryDirectory() as directory:
            environment = deferred_environment(directory)
            started = start_deferred(defer, directory, environment, "pass")
            task_dir = Path(json.loads(started.stdout)["task_dir"])
            wait_for_result(task_dir)

            for attempt in range(1, 4):
                if attempt > 1:
                    time.sleep(0.03)
                wake = invoke_stop(stop_hook, environment)
                self.assertEqual(wake["decision"], "block")
                self.assertIn("resume --task-dir", str(wake["reason"]))
                wake_state = json.loads(
                    (task_dir / "wake.json").read_text(encoding="utf-8")
                )
                self.assertEqual(wake_state["attempt"], attempt)

            released = invoke_stop(stop_hook, environment)
            self.assertEqual(released, {"continue": True})
            self.assertFalse((task_dir / "ack.json").exists())

    def test_deferred_legacy_wake_counts_as_first_delivery(self) -> None:
        defer, stop_hook = deferred_paths()
        with tempfile.TemporaryDirectory() as directory:
            environment = deferred_environment(directory)
            started = start_deferred(defer, directory, environment, "pass")
            task_dir = Path(json.loads(started.stdout)["task_dir"])
            wait_for_result(task_dir)
            (task_dir / "wake.json").write_text(
                json.dumps(
                    {
                        "emitted_at": "2000-01-01T00:00:00+00:00",
                        "exit_code": 0,
                    }
                ),
                encoding="utf-8",
            )

            wake = invoke_stop(stop_hook, environment)
            self.assertEqual(wake["decision"], "block")
            wake_state = json.loads(
                (task_dir / "wake.json").read_text(encoding="utf-8")
            )
            self.assertEqual(wake_state["attempt"], 2)


if __name__ == "__main__":
    unittest.main()
