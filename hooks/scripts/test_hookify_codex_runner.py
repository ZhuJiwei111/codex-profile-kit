#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("hookify_codex_runner.py")
PROFILE_RULES = Path(__file__).resolve().parent.parent / "rules"
ACTIVE_RULES = Path.home() / ".codex" / "hookify"
SOURCE_RULES = PROFILE_RULES if PROFILE_RULES.is_dir() else ACTIVE_RULES


class HookifyCodexRunnerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / "home"
        self.project = self.root / "project"
        self.rules = self.home / ".codex" / "hookify"
        self.rules.parent.mkdir(parents=True)
        self.project.mkdir()
        shutil.copytree(SOURCE_RULES, self.rules)

    def payload(self, tool_name: str, command: str, cwd: Path | None = None) -> dict[str, object]:
        return {
            "session_id": "test-session",
            "transcript_path": None,
            "cwd": str(cwd or self.project),
            "hook_event_name": "PreToolUse",
            "model": "test-model",
            "permission_mode": "default",
            "turn_id": "test-turn",
            "tool_name": tool_name,
            "tool_input": {"command": command},
            "tool_use_id": "test-call",
        }

    def invoke(self, event: dict[str, object]) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["HOME"] = str(self.home)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--event", "PreToolUse"],
            input=json.dumps(event),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=True,
        )

    def output_json(self, result: subprocess.CompletedProcess[str]) -> dict[str, object]:
        self.assertTrue(result.stdout.strip(), "expected JSON hook output")
        value = json.loads(result.stdout)
        self.assertIsInstance(value, dict)
        return value

    def hook_output(self, result: subprocess.CompletedProcess[str]) -> dict[str, object]:
        value = self.output_json(result).get("hookSpecificOutput")
        self.assertIsInstance(value, dict)
        return value

    def assert_denied(self, result: subprocess.CompletedProcess[str], label: str) -> None:
        output = self.hook_output(result)
        self.assertEqual(output.get("hookEventName"), "PreToolUse")
        self.assertEqual(output.get("permissionDecision"), "deny")
        self.assertIn(label, str(output.get("permissionDecisionReason")))

    def assert_context(self, result: subprocess.CompletedProcess[str], label: str) -> None:
        output = self.hook_output(result)
        self.assertEqual(output.get("hookEventName"), "PreToolUse")
        self.assertNotIn("permissionDecision", output)
        self.assertIn(label, str(output.get("additionalContext")))

    def patch(self, *paths: str, added_line: str = "+new") -> str:
        chunks = ["*** Begin Patch"]
        for path in paths:
            chunks.extend(
                [
                    f"*** Update File: {path}",
                    "@@",
                    "-old",
                    added_line,
                ]
            )
        chunks.append("*** End Patch")
        return "\n".join(chunks)

    def test_real_apply_patch_sensitive_path_is_denied(self) -> None:
        result = self.invoke(
            self.payload(
                "apply_patch",
                self.patch("/root/.codex/auth.json"),
            )
        )

        self.assert_denied(result, "block-sensitive-file-edits")

    def test_multi_file_patch_denies_when_any_path_is_hard_sensitive(self) -> None:
        result = self.invoke(
            self.payload(
                "apply_patch",
                self.patch("docs/guide.md", "/root/.ssh/id_ed25519"),
            )
        )

        self.assert_denied(result, "block-sensitive-file-edits")

    def test_env_file_edit_is_left_to_agents_policy(self) -> None:
        result = self.invoke(self.payload("apply_patch", self.patch(".env")))

        self.assertEqual(result.stdout, "")

    def test_env_example_edit_is_silent(self) -> None:
        result = self.invoke(self.payload("apply_patch", self.patch(".env.example")))

        self.assertEqual(result.stdout, "")

    def test_public_pem_edit_is_silent_but_private_pem_is_denied(self) -> None:
        public_result = self.invoke(
            self.payload("apply_patch", self.patch("certificates/server.pem"))
        )
        private_result = self.invoke(
            self.payload("apply_patch", self.patch("certificates/private-key.pem"))
        )

        self.assertEqual(public_result.stdout, "")
        self.assert_denied(private_result, "block-sensitive-file-edits")

    def test_apply_patch_content_does_not_match_bash_rules(self) -> None:
        result = self.invoke(
            self.payload(
                "apply_patch",
                self.patch("docs/guide.md", added_line='+ "conda install demo -n base"'),
            )
        )

        self.assertEqual(result.stdout, "")

    def test_bash_patch_header_text_does_not_match_file_rules(self) -> None:
        command = "printf '%s\\n' '*** Update File: /root/.codex/auth.json'"
        result = self.invoke(self.payload("Bash", command))

        self.assertEqual(result.stdout, "")

    def test_package_install_is_left_to_agents_policy(self) -> None:
        result = self.invoke(self.payload("Bash", "pip install -r requirements.txt"))

        self.assertEqual(result.stdout, "")

    def test_explicit_base_conda_install_is_denied(self) -> None:
        result = self.invoke(self.payload("Bash", "conda install demo -n base"))

        self.assert_denied(result, "block-base-conda-install")

    def test_explicit_base_conda_env_create_is_denied(self) -> None:
        result = self.invoke(self.payload("Bash", "conda env create -n base -f env.yml"))

        self.assert_denied(result, "block-base-conda-install")

    def test_explicit_base_prefix_install_is_denied(self) -> None:
        commands = (
            "mamba install -p /example/miniconda3 demo",
            'conda install --prefix="/example/anaconda3" demo',
        )

        for command in commands:
            with self.subTest(command=command):
                result = self.invoke(self.payload("Bash", command))
                self.assert_denied(result, "block-base-conda-install")

    def test_project_conda_install_is_silent_without_base_deny(self) -> None:
        result = self.invoke(self.payload("Bash", "conda install demo -n project-env"))

        self.assertEqual(result.stdout, "")

    def test_documented_fallback_install_is_silent_without_base_deny(self) -> None:
        result = self.invoke(
            self.payload(
                "Bash",
                "mamba install -p /example/conda/envs/codex-tools demo",
            )
        )

        self.assertEqual(result.stdout, "")

    def test_sensitive_shell_mutation_is_denied(self) -> None:
        result = self.invoke(
            self.payload("Bash", "printf rotated > /root/.codex/auth.json")
        )

        self.assert_denied(result, "block-sensitive-path-command")

    def test_sensitive_metadata_read_is_left_to_agents_policy(self) -> None:
        result = self.invoke(self.payload("Bash", "stat /root/.codex/auth.json"))

        self.assertEqual(result.stdout, "")

    def test_project_markdown_rules_are_not_loaded(self) -> None:
        project_rules = self.project / ".codex" / "hookify"
        project_rules.mkdir(parents=True)
        (project_rules / "block-project-command.md").write_text(
            """---
name: block-project-command
enabled: true
event: bash
action: block
pattern: harmless-command
---

Project rule should not be loaded by the global adapter.
""",
            encoding="utf-8",
        )

        result = self.invoke(self.payload("Bash", "harmless-command"))

        self.assertEqual(result.stdout, "")

    def test_invalid_global_regex_does_not_corrupt_valid_deny_json(self) -> None:
        (self.rules / "invalid-regex.md").write_text(
            """---
name: invalid-regex
enabled: true
event: file
action: warn
pattern: [unterminated
---

Invalid test rule.
""",
            encoding="utf-8",
        )

        result = self.invoke(
            self.payload("apply_patch", self.patch("/root/.codex/auth.json"))
        )

        self.assert_denied(result, "block-sensitive-file-edits")
        self.assertIn("invalid-regex.md", result.stderr)

    def test_gpu_launch_without_scope_is_left_to_agents_policy(self) -> None:
        result = self.invoke(
            self.payload("Bash", "tmux new-session -d python3 train_model.py")
        )

        self.assertEqual(result.stdout, "")

    def test_scoped_detached_gpu_launch_is_silent(self) -> None:
        command = "CUDA_VISIBLE_DEVICES=0 tmux new-session -d python3 train_model.py"
        result = self.invoke(self.payload("Bash", command))

        self.assertEqual(result.stdout, "")

    def test_attached_long_job_launch_is_left_to_agents_policy(self) -> None:
        command = "CUDA_VISIBLE_DEVICES=0 python3 train_model.py"
        result = self.invoke(self.payload("Bash", command))

        self.assertEqual(result.stdout, "")

    def test_continuous_monitoring_is_left_to_agents_policy(self) -> None:
        result = self.invoke(self.payload("Bash", "tail -f training.log"))

        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
