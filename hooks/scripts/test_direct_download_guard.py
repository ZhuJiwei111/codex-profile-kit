#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).with_name("direct_download_guard.py")
PROXY_VARS = (
    "HTTPS_PROXY",
    "HTTP_PROXY",
    "ALL_PROXY",
    "https_proxy",
    "http_proxy",
    "all_proxy",
)


class DirectDownloadGuardTest(unittest.TestCase):
    def payload(self, command: str, tool_name: str = "Bash") -> dict[str, object]:
        return {
            "session_id": "test-session",
            "transcript_path": None,
            "cwd": "/tmp/test-project",
            "hook_event_name": "PreToolUse",
            "model": "test-model",
            "permission_mode": "default",
            "turn_id": "test-turn",
            "tool_name": tool_name,
            "tool_input": {"command": command},
            "tool_use_id": "test-call",
        }

    def invoke(self, command: str, tool_name: str = "Bash") -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        for name in PROXY_VARS:
            env[name] = "http://proxy.example.test:8080"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps(self.payload(command, tool_name)),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=True,
        )

    def assert_denied(self, result: subprocess.CompletedProcess[str]) -> None:
        value = json.loads(result.stdout)
        output = value["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "PreToolUse")
        self.assertEqual(output["permissionDecision"], "deny")
        self.assertTrue(output["permissionDecisionReason"])

    def test_blocks_large_download_with_inherited_proxy(self) -> None:
        result = self.invoke("wget https://example.test/models/model.bin -O models/model.bin")

        self.assert_denied(result)

    def test_direct_env_wrapper_allows_download(self) -> None:
        unset_flags = " ".join(f"-u {name}" for name in PROXY_VARS)
        result = self.invoke(
            f"env {unset_flags} wget https://example.test/models/model.bin -O models/model.bin"
        )

        self.assertEqual(result.stdout, "")

    def test_proxy_off_wrapper_allows_download(self) -> None:
        result = self.invoke(
            "proxy_off wget https://example.test/models/model.bin -O models/model.bin"
        )

        self.assertEqual(result.stdout, "")

    def test_unrelated_env_wrapper_does_not_allow_later_download(self) -> None:
        unset_flags = " ".join(f"-u {name}" for name in PROXY_VARS)
        result = self.invoke(
            f"env {unset_flags} true; "
            "wget https://example.test/models/model.bin -O models/model.bin"
        )

        self.assert_denied(result)

    def test_unexecuted_unset_does_not_allow_later_download(self) -> None:
        unset_vars = " ".join(PROXY_VARS)
        result = self.invoke(
            f"false && unset {unset_vars}; "
            "wget https://example.test/models/model.bin -O models/model.bin"
        )

        self.assert_denied(result)

    def test_proxy_off_for_other_command_does_not_allow_later_download(self) -> None:
        result = self.invoke(
            "proxy_off true; wget https://example.test/models/model.bin -O models/model.bin"
        )

        self.assert_denied(result)

    def test_approved_proxy_marker_allows_download(self) -> None:
        result = self.invoke(
            "CODEX_APPROVED_PROXY_DOWNLOAD=1 "
            "wget https://example.test/models/model.bin -O models/model.bin"
        )

        self.assertEqual(result.stdout, "")

    def test_aws_listing_is_not_treated_as_transfer(self) -> None:
        result = self.invoke("aws s3 ls s3://example/models/")

        self.assertEqual(result.stdout, "")

    def test_aws_copy_of_large_artifact_is_blocked(self) -> None:
        result = self.invoke("aws s3 cp s3://example/model.bin models/model.bin")

        self.assert_denied(result)

    def test_package_install_is_not_a_hard_download_guard(self) -> None:
        result = self.invoke("pip install -r requirements.txt")

        self.assertEqual(result.stdout, "")

    def test_small_metadata_curl_is_silent(self) -> None:
        result = self.invoke("curl -fsS https://example.test/metadata.json")

        self.assertEqual(result.stdout, "")

    def test_non_bash_payload_is_ignored(self) -> None:
        patch = "*** Begin Patch\n*** Update File: docs/example.md\n*** End Patch"
        result = self.invoke(patch, tool_name="apply_patch")

        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
