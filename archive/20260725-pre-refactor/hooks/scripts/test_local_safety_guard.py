#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).with_name("local_safety_guard.py")


class LocalSafetyGuardTest(unittest.TestCase):
    def payload(self, tool_name: str, command: str) -> dict[str, object]:
        return {
            "hook_event_name": "PreToolUse",
            "tool_name": tool_name,
            "tool_input": {"command": command},
            "tool_use_id": "test-call",
        }

    def invoke(self, tool_name: str, command: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps(self.payload(tool_name, command)),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    def assert_denied(
        self, result: subprocess.CompletedProcess[str], *labels: str
    ) -> None:
        value = json.loads(result.stdout)
        output = value["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "PreToolUse")
        self.assertEqual(output["permissionDecision"], "deny")
        for label in labels:
            self.assertIn(label, output["permissionDecisionReason"])

    def patch(self, *paths: str, added_line: str = "+new") -> str:
        chunks = ["*** Begin Patch"]
        for path in paths:
            chunks.extend([f"*** Update File: {path}", "@@", "-old", added_line])
        chunks.append("*** End Patch")
        return "\n".join(chunks)

    def test_apply_patch_denies_exact_sensitive_categories(self) -> None:
        for path in (
            "/root/.codex/auth.json",
            "/root/.codex/sessions/item.json",
            "/root/.ssh/id_ed25519",
            "/root/.netrc",
            "certificates/private-key.pem",
            "secrets/client.key",
        ):
            with self.subTest(path=path):
                self.assert_denied(
                    self.invoke("apply_patch", self.patch(path)),
                    "sensitive-file-edit",
                )

    def test_multi_file_patch_denies_when_one_path_is_sensitive(self) -> None:
        result = self.invoke(
            "apply_patch", self.patch("docs/guide.md", "/root/.codex/auth.json")
        )

        self.assert_denied(result, "sensitive-file-edit")

    def test_non_sensitive_patch_and_sensitive_text_in_content_are_silent(self) -> None:
        commands = (
            self.patch(".env"),
            self.patch(".env.example"),
            self.patch("certificates/server.pem"),
            self.patch("docs/guide.md", added_line="+ /root/.codex/auth.json"),
        )

        for command in commands:
            with self.subTest(command=command):
                self.assertEqual(self.invoke("apply_patch", command).stdout, "")

    def test_explicit_conda_base_mutations_are_denied(self) -> None:
        commands = (
            "conda install demo -n base",
            "conda env create --name=base -f env.yml",
            "mamba install -p /example/miniconda3 demo",
            "conda run -n base python -m pip install demo",
            "conda activate base && pip install demo",
        )

        for command in commands:
            with self.subTest(command=command):
                self.assert_denied(
                    self.invoke("Bash", command), "conda-base-install"
                )

    def test_project_environment_and_other_installers_are_silent(self) -> None:
        commands = (
            "conda install demo -n project-env",
            "mamba install -p /example/conda/envs/codex-tools demo",
            "pip install -r requirements.txt",
        )

        for command in commands:
            with self.subTest(command=command):
                self.assertEqual(self.invoke("Bash", command).stdout, "")

    def test_sensitive_shell_mutations_are_denied_but_reads_are_silent(self) -> None:
        mutations = (
            "printf rotated > /root/.codex/auth.json",
            "rm /root/.ssh/id_ed25519",
            "sed -i 's/x/y/' /root/.netrc",
        )
        for command in mutations:
            with self.subTest(command=command):
                self.assert_denied(
                    self.invoke("Bash", command), "sensitive-path-mutation"
                )

        for command in (
            "stat /root/.codex/auth.json",
            "printf '%s\\n' '*** Update File: /root/.codex/auth.json'",
        ):
            with self.subTest(command=command):
                self.assertEqual(self.invoke("Bash", command).stdout, "")

    def test_conflicting_matches_return_one_valid_combined_denial(self) -> None:
        result = self.invoke(
            "Bash",
            "conda install demo -n base; printf rotated > /root/.codex/auth.json",
        )

        self.assert_denied(
            result, "conda-base-install", "sensitive-path-mutation"
        )

    def test_non_matching_tool_is_silent(self) -> None:
        self.assertEqual(self.invoke("Read", "conda install demo -n base").stdout, "")

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
