#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("smart_commit_stage.py")


def run(args: list[str], cwd: Path, **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **kwargs,
    )


class SmartCommitStageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.state_path = self.base / "pending.json"

        run(["git", "init"], self.repo, check=True)
        run(["git", "config", "user.email", "codex@example.test"], self.repo, check=True)
        run(["git", "config", "user.name", "Codex Test"], self.repo, check=True)
        (self.repo / "file.txt").write_text("old\n", encoding="utf-8")
        run(["git", "add", "file.txt"], self.repo, check=True)
        run(["git", "commit", "-m", "initial"], self.repo, check=True)
        (self.repo / "file.txt").write_text("new\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def invoke(self, mode: str, event: dict[str, object]) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["SMART_COMMIT_PENDING_PATH"] = str(self.state_path)
        return run(
            [sys.executable, str(SCRIPT), "--mode", mode],
            self.repo,
            input=json.dumps(event),
            env=env,
            check=True,
        )

    def assert_file_not_staged(self) -> None:
        result = run(["git", "diff", "--cached", "--quiet", "--", "file.txt"], self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)

    def assert_file_staged(self) -> None:
        result = run(["git", "diff", "--cached", "--quiet", "--", "file.txt"], self.repo)
        self.assertNotEqual(result.returncode, 0)

    def test_record_mode_tracks_touched_file_without_staging(self) -> None:
        self.invoke("record", {"cwd": str(self.repo), "tool_input": {"file_path": "file.txt"}})

        self.assert_file_not_staged()
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["repos"][str(self.repo)]["paths"], ["file.txt"])

    def test_confirm_mode_stages_pending_file_after_acceptance_prompt(self) -> None:
        self.invoke("record", {"cwd": str(self.repo), "tool_input": {"file_path": "file.txt"}})

        result = self.invoke("confirm", {"cwd": str(self.repo), "user_prompt": "验收通过，可以暂存"})

        self.assert_file_staged()
        self.assertIn("About to stage current changes", result.stdout)
        self.assertIn("M file.txt", result.stdout)
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["repos"], {})

    def test_confirm_mode_ignores_non_acceptance_prompt(self) -> None:
        self.invoke("record", {"cwd": str(self.repo), "tool_input": {"file_path": "file.txt"}})

        self.invoke("confirm", {"cwd": str(self.repo), "user_prompt": "先继续检查，不要暂存"})

        self.assert_file_not_staged()

    def test_confirm_mode_does_not_stage_for_final_answer_prompt(self) -> None:
        self.invoke("record", {"cwd": str(self.repo), "tool_input": {"file_path": "file.txt"}})

        self.invoke("confirm", {"cwd": str(self.repo), "user_prompt": "请提交最终答案"})

        self.assert_file_not_staged()

    def test_confirm_mode_does_not_stage_for_stage_number_prompt(self) -> None:
        self.invoke("record", {"cwd": str(self.repo), "tool_input": {"file_path": "file.txt"}})

        self.invoke("confirm", {"cwd": str(self.repo), "user_prompt": "继续看 stage 2 的输出"})

        self.assert_file_not_staged()


if __name__ == "__main__":
    unittest.main()
