import json
import os
from pathlib import Path
import selectors
import subprocess
import tempfile
import time
import unittest


if os.environ.get("PLJS_RUN_SYSTEMD_TESTS") != "1":
    raise unittest.SkipTest("set PLJS_RUN_SYSTEMD_TESTS=1 to run user-systemd integration tests")

import sys

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))
from supervisor import JobStore  # noqa: E402


class SystemdIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = JobStore(Path(self.tmp.name) / "state")

    def tearDown(self):
        self.tmp.cleanup()

    def start(self, name, code, **kwargs):
        return self.store.start_job(
            name=name,
            cwd=self.tmp.name,
            command=[sys.executable, "-c", code],
            **kwargs,
        )

    def ack_and_clean(self, job_id, event):
        self.store.ack_event(job_id, event["event_id"])
        deadline = time.time() + 5
        while time.time() < deadline:
            observed = self.store.inspect_job(job_id)
            if observed["unit_state"].get("ActiveState") != "active":
                self.store.clean_job(job_id)
                return
            time.sleep(0.05)
        self.fail("systemd unit did not become inactive")

    def test_normal_failure_and_large_log(self):
        normal = self.start("normal", "import time; time.sleep(0.2); print('ok')")
        failed = self.start("failed", "import sys,time; time.sleep(0.2); sys.exit(9)")
        marker = "LOG-MUST-STAY-OUTSIDE-CONTEXT"
        large = self.start("large-log", f"print('{marker}' + 'x' * 30000)")

        normal_event = self.store.wait_event(normal["job_id"], poll_interval=0.05)
        failed_event = self.store.wait_event(failed["job_id"], poll_interval=0.05)
        large_event = self.store.wait_event(large["job_id"], poll_interval=0.05)

        self.assertEqual("completed", normal_event["event_type"])
        self.assertEqual("failed", failed_event["event_type"])
        self.assertEqual(9, failed_event["exit_code"])
        self.assertNotIn(marker, self.store.render_payload(large_event))
        self.assertIn(marker, (self.store.job_dir(large["job_id"]) / "combined.log").read_text())
        for job, event in ((normal, normal_event), (failed, failed_event), (large, large_event)):
            self.ack_and_clean(job["job_id"], event)

    def test_stale_heartbeat_reports_attention_without_stopping_job(self):
        heartbeat = Path(self.tmp.name) / "heartbeat"
        heartbeat.touch()
        job = self.start(
            "heartbeat",
            "import time; time.sleep(1.5)",
            heartbeat_path=heartbeat,
            stale_after=0.3,
        )

        event = self.store.wait_event(job["job_id"], poll_interval=0.05)
        observed = self.store.inspect_job(job["job_id"])

        self.assertEqual("attention", event["event_type"])
        self.assertEqual("active", observed["unit_state"]["ActiveState"])
        self.store.ack_event(job["job_id"], event["event_id"])
        terminal = self.store.wait_event(job["job_id"], poll_interval=0.05)
        self.assertEqual("completed", terminal["event_type"])
        self.ack_and_clean(job["job_id"], terminal)

    def test_mcp_process_can_die_and_reconnect_without_stopping_job(self):
        job = self.start("mcp-reconnect", "import time; time.sleep(0.8)")
        env = os.environ.copy()
        env["PLJS_STATE_ROOT"] = str(self.store.state_root)
        env["PLJS_POLL_INTERVAL_SECONDS"] = "0.05"
        command = [sys.executable, str(PLUGIN_ROOT / "scripts" / "mcp_server.py")]

        first = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        wait_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "wait_event", "arguments": {"job_id": job["job_id"]}},
        }
        first.stdin.write(json.dumps(wait_request) + "\n")
        first.stdin.flush()
        first.terminate()
        first.wait(timeout=5)
        for stream in (first.stdin, first.stdout, first.stderr):
            stream.close()

        second = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        second.stdin.write(json.dumps(wait_request) + "\n")
        second.stdin.flush()
        selector = selectors.DefaultSelector()
        selector.register(second.stdout, selectors.EVENT_READ)
        ready = selector.select(timeout=5)
        selector.close()
        self.assertTrue(ready, "reconnected MCP did not receive the durable event")
        response = json.loads(second.stdout.readline())
        second.terminate()
        second.wait(timeout=5)
        for stream in (second.stdin, second.stdout, second.stderr):
            stream.close()

        event = response["result"]["structuredContent"]
        self.assertEqual("completed", event["event_type"])
        self.ack_and_clean(job["job_id"], event)
