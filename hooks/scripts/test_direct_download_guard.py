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
    def invoke(self, command: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        for name in PROXY_VARS:
            env[name] = "http://proxy.example.test:8080"
        event = {"tool_name": "Bash", "tool_input": {"command": command}}
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps(event),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=True,
        )

    def test_blocks_large_download_with_inherited_proxy(self) -> None:
        result = self.invoke("wget https://example.test/models/model.bin -O models/model.bin")

        self.assertIn("permissionDecision", result.stdout)
        self.assertIn("deny", result.stdout)

    def test_blocks_download_when_only_one_proxy_var_is_unset(self) -> None:
        result = self.invoke(
            "env -u HTTPS_PROXY wget https://example.test/models/model.bin -O models/model.bin"
        )

        self.assertIn("permissionDecision", result.stdout)
        self.assertIn("deny", result.stdout)

    def test_all_proxy_unsets_allow_direct_download(self) -> None:
        unset_flags = " ".join(f"-u {name}" for name in PROXY_VARS)
        result = self.invoke(
            f"env {unset_flags} wget https://example.test/models/model.bin -O models/model.bin"
        )

        self.assertEqual(result.stdout, "")

    def test_proxy_unsets_after_download_do_not_allow_download(self) -> None:
        unset_vars = " ".join(PROXY_VARS)
        result = self.invoke(
            "wget https://example.test/models/model.bin -O models/model.bin; "
            f"unset {unset_vars}"
        )

        self.assertIn("permissionDecision", result.stdout)
        self.assertIn("deny", result.stdout)

    def test_proxy_off_prefix_allows_direct_download(self) -> None:
        result = self.invoke(
            "proxy_off wget https://example.test/models/model.bin -O models/model.bin"
        )

        self.assertEqual(result.stdout, "")

    def test_proxy_off_after_download_does_not_allow_download(self) -> None:
        result = self.invoke(
            "wget https://example.test/models/model.bin -O models/model.bin; proxy_off"
        )

        self.assertIn("permissionDecision", result.stdout)
        self.assertIn("deny", result.stdout)


if __name__ == "__main__":
    unittest.main()
