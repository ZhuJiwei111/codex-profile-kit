import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
import threading
import time
import unittest


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

from supervisor import JobStore  # noqa: E402


class DetachedProcessIntegrationTest(unittest.TestCase):
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
            if not observed["process_state"]["active"]:
                self.store.clean_job(job_id)
                return
            time.sleep(0.02)
        self.fail("detached worker did not become inactive")

    def test_process_identity_and_atomic_terminal_result(self):
        job = self.start("identity", "import time; time.sleep(0.3)")

        registration = json.loads(
            (self.store.job_dir(job["job_id"]) / "job.json").read_text(encoding="utf-8")
        )
        process = registration["process"]
        self.assertGreater(process["pid"], 0)
        self.assertGreater(process["start_ticks"], 0)
        self.assertTrue(job["process_state"]["identity_matches"])
        self.assertEqual("running", job["status"])

        event = self.store.wait_event(job["job_id"], poll_interval=0.02)
        self.assertEqual("completed", event["event_type"])
        self.assertEqual(0, event["exit_code"])
        self.ack_and_clean(job["job_id"], event)
        self.assertFalse(self.store.job_dir(job["job_id"]).exists())

    def test_worker_survives_launcher_exit_and_reconnects_from_disk(self):
        state_root = Path(self.tmp.name) / "cli-state"
        command = [
            sys.executable,
            str(PLUGIN_ROOT / "scripts" / "supervisor.py"),
            "--state-root",
            str(state_root),
            "start",
            "--name",
            "launcher-exit",
            "--cwd",
            self.tmp.name,
            "--",
            sys.executable,
            "-c",
            "import time; time.sleep(0.2)",
        ]

        launched = subprocess.run(command, text=True, capture_output=True, check=False)

        self.assertEqual(0, launched.returncode, launched.stderr)
        job_id = json.loads(launched.stdout)["job_id"]
        reconnected = JobStore(state_root)
        event = reconnected.wait_event(job_id, poll_interval=0.02)
        self.assertEqual("completed", event["event_type"])
        reconnected.ack_event(job_id, event["event_id"])
        deadline = time.time() + 5
        while reconnected.inspect_job(job_id)["process_state"]["active"]:
            self.assertLess(time.time(), deadline, "detached worker stayed active")
            time.sleep(0.02)
        reconnected.clean_job(job_id)

    def test_failure_and_large_log_stay_bounded(self):
        failed = self.start("failed", "import sys; sys.exit(9)")
        marker = "LOG-MUST-STAY-OUTSIDE-CONTEXT"
        large = self.start("large-log", f"print('{marker}' + 'x' * 30000)")

        failed_event = self.store.wait_event(failed["job_id"], poll_interval=0.02)
        large_event = self.store.wait_event(large["job_id"], poll_interval=0.02)

        self.assertEqual("failed", failed_event["event_type"])
        self.assertEqual(9, failed_event["exit_code"])
        self.assertNotIn(marker, self.store.render_payload(large_event))
        self.assertIn(
            marker,
            (self.store.job_dir(large["job_id"]) / "combined.log").read_text(),
        )
        self.ack_and_clean(failed["job_id"], failed_event)
        self.ack_and_clean(large["job_id"], large_event)

    def test_stale_heartbeat_reports_attention_without_stopping_job(self):
        heartbeat = Path(self.tmp.name) / "heartbeat"
        heartbeat.touch()
        job = self.start(
            "heartbeat",
            "import time; time.sleep(3)",
            heartbeat_path=heartbeat,
            stale_after=0.1,
        )

        event = self.store.wait_event(job["job_id"], poll_interval=0.02)
        observed = self.store.inspect_job(job["job_id"])

        self.assertEqual("attention", event["event_type"])
        self.assertTrue(observed["process_state"]["active"])
        self.store.ack_event(job["job_id"], event["event_id"])
        terminal = self.store.wait_event(job["job_id"], poll_interval=0.02)
        self.assertEqual("completed", terminal["event_type"])
        self.ack_and_clean(job["job_id"], terminal)

    def test_mcp_process_can_die_and_reconnect_without_stopping_job(self):
        job = self.start("mcp-reconnect", "import time; time.sleep(0.3)")
        environment = os.environ.copy()
        environment["PLJS_STATE_ROOT"] = str(self.store.state_root)
        environment["PLJS_POLL_INTERVAL_SECONDS"] = "0.02"
        command = [sys.executable, str(PLUGIN_ROOT / "scripts" / "mcp_server.py")]
        wait_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "wait_event", "arguments": {"job_id": job["job_id"]}},
        }

        first = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=environment,
        )
        first.stdin.write(json.dumps(wait_request) + "\n")
        first.stdin.flush()
        first.terminate()
        first.wait(timeout=5)
        for stream in (first.stdin, first.stdout, first.stderr):
            stream.close()

        second = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=environment,
        )
        second.stdin.write(json.dumps(wait_request) + "\n")
        second.stdin.flush()
        responses = queue.Queue()
        reader = threading.Thread(target=lambda: responses.put(second.stdout.readline()), daemon=True)
        reader.start()
        try:
            response = json.loads(responses.get(timeout=5))
        except queue.Empty:
            self.fail("reconnected MCP did not receive the durable event")
        second.terminate()
        second.wait(timeout=5)
        for stream in (second.stdin, second.stdout, second.stderr):
            stream.close()

        event = response["result"]["structuredContent"]
        self.assertEqual("completed", event["event_type"])
        self.ack_and_clean(job["job_id"], event)

    def test_health_attention_persists_while_mcp_is_disconnected(self):
        heartbeat = Path(self.tmp.name) / "detached-heartbeat"
        heartbeat.touch()
        monitor = json.dumps(
            {
                "kind": "heartbeat_stale",
                "path": str(heartbeat),
                "stale_after_seconds": 0.15,
                "sample_interval_seconds": 0.05,
            }
        )
        job = self.start(
            "health-reconnect",
            "import time; time.sleep(0.7)",
            monitors=[monitor],
        )
        environment = os.environ.copy()
        environment["PLJS_STATE_ROOT"] = str(self.store.state_root)
        command = [sys.executable, str(PLUGIN_ROOT / "scripts" / "mcp_server.py")]

        disconnected = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=environment,
        )
        disconnected.terminate()
        disconnected.wait(timeout=5)
        for stream in (disconnected.stdin, disconnected.stdout, disconnected.stderr):
            stream.close()

        deadline = time.time() + 3
        events_path = self.store.job_dir(job["job_id"]) / "events.json"
        while time.time() < deadline:
            events = json.loads(events_path.read_text(encoding="utf-8"))["events"]
            if any(event.get("reason") == "heartbeat_stale" for event in events):
                break
            time.sleep(0.02)
        else:
            self.fail("worker did not persist health attention while MCP was absent")

        reconnected = JobStore(self.store.state_root)
        event = reconnected.wait_event(job["job_id"], poll_interval=0.02)
        self.assertEqual("attention", event["event_type"])
        self.assertEqual("heartbeat_stale", event["reason"])
        self.assertEqual("job_declared_path", event["scope"])
        reconnected.ack_event(job["job_id"], event["event_id"])
        terminal = reconnected.wait_event(job["job_id"], poll_interval=0.02)
        self.assertEqual("completed", terminal["event_type"])
        self.ack_and_clean(job["job_id"], terminal)


if __name__ == "__main__":
    unittest.main()
