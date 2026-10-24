from __future__ import annotations

import os
from pathlib import Path
import sys
import unittest
from unittest import mock


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import process_identity  # noqa: E402


class ProcessIdentityTest(unittest.TestCase):
    def test_windows_dispatches_to_windows_identity(self) -> None:
        expected = {"pid": 123, "start_ticks": 456, "state_code": "R"}
        with mock.patch.object(process_identity.sys, "platform", "win32"), mock.patch.object(
            process_identity, "_windows_identity", return_value=expected
        ) as windows_identity:
            observed = process_identity.process_identity(123)

        self.assertEqual(expected, observed)
        windows_identity.assert_called_once_with(123)

    @unittest.skipUnless(sys.platform == "win32", "Windows process API test")
    def test_windows_identity_distinguishes_current_process(self) -> None:
        first = process_identity.process_identity(os.getpid())
        second = process_identity.process_identity(os.getpid())

        self.assertIsNotNone(first)
        self.assertEqual(first, second)
        self.assertGreater(first["start_ticks"], 0)


if __name__ == "__main__":
    unittest.main()
