#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).with_name("direct_download_guard.py")
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
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps(self.payload(command, tool_name)),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    def assert_warned(self, result: subprocess.CompletedProcess[str]) -> dict[str, object]:
        self.assertNotEqual(result.stdout, "", "expected one warning JSON object")
        value = json.loads(result.stdout)
        output = value["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "PreToolUse")
        self.assertNotIn("permissionDecision", output)
        self.assertTrue(output["additionalContext"])
        return output

    def test_warns_for_likely_large_download_without_reading_proxy_state(self) -> None:
        result = self.invoke("wget https://example.test/models/model.bin -O models/model.bin")

        output = self.assert_warned(result)
        context = str(output["additionalContext"])
        self.assertIn("small direct probe", context)
        self.assertIn("HOST_LOCAL", context)
        self.assertIn("authorization", context)

    def test_explicit_env_wrapper_does_not_suppress_stateless_advice(self) -> None:
        result = self.invoke(
            "env -u HTTPS_PROXY wget https://example.test/models/model.bin -O models/model.bin"
        )

        self.assert_warned(result)

    def test_proxy_off_text_is_not_a_portable_direct_path_bypass(self) -> None:
        result = self.invoke(
            "proxy_off wget https://example.test/models/model.bin -O models/model.bin"
        )

        self.assert_warned(result)

    def test_proxy_off_for_other_command_does_not_allow_later_download(self) -> None:
        result = self.invoke(
            "proxy_off true; wget https://example.test/models/model.bin -O models/model.bin"
        )

        self.assert_warned(result)

    def test_aws_listing_is_not_treated_as_transfer(self) -> None:
        result = self.invoke("aws s3 ls s3://example/models/")

        self.assertEqual(result.stdout, "")

    def test_aws_copy_of_large_artifact_warns(self) -> None:
        result = self.invoke("aws s3 cp s3://example/model.bin models/model.bin")

        self.assert_warned(result)

    def test_package_install_is_not_a_hard_download_guard(self) -> None:
        result = self.invoke("pip install -r requirements.txt")

        self.assertEqual(result.stdout, "")

    def test_small_metadata_curl_is_silent(self) -> None:
        result = self.invoke("curl -fsS https://example.test/metadata.json")

        self.assertEqual(result.stdout, "")

    def test_wget_spider_probe_is_silent(self) -> None:
        result = self.invoke("wget --spider https://example.test/models/model.bin")

        self.assertEqual(result.stdout, "")

    def test_non_bash_payload_is_ignored(self) -> None:
        patch = "*** Begin Patch\n*** Update File: docs/example.md\n*** End Patch"
        result = self.invoke(patch, tool_name="apply_patch")

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
