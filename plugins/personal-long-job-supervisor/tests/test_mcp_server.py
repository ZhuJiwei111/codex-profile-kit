import json
import os
from datetime import datetime, timezone
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
import threading
import time
import unittest


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import mcp_server  # noqa: E402
from supervisor import JobStore  # noqa: E402
from process_identity import require_process_identity  # noqa: E402


class FakeRuntime:
    def start(self, registration, worker_path, python_executable):
        return {"pid": 1234, "start_ticks": 5678}

    def inspect(self, process):
        return {
            **process,
            "observed_start_ticks": process["start_ticks"],
            "identity_matches": True,
            "active": True,
            "state": "running",
        }

class McpObservationContractTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = JobStore(Path(self.tmp.name) / "state", runtime=FakeRuntime())
        self.cwd = Path(self.tmp.name) / "work"
        self.cwd.mkdir()
        mcp_server.STORE = self.store

    def tearDown(self):
        self.tmp.cleanup()

    def test_exposes_only_observation_wait_control_and_ack_tools(self):
        self.assertEqual(
            {"wait_event", "wait_any", "interrupt_wait", "inspect_job", "list_jobs", "ack_event", "get_capabilities"},
            set(mcp_server.TOOL_NAMES),
        )

    def test_capabilities_does_not_require_job_store(self):
        mcp_server.STORE = None
        payload = json.loads(mcp_server.get_capabilities())
        self.assertEqual(1, payload["schema_version"])
        self.assertIn("gpu_process_idle", payload["monitors"])

    def test_wait_event_and_ack_are_bounded_json(self):
        job = self.store.start_job(name="mcp", cwd=self.cwd, command=["/bin/true"])
        self.store._atomic_write_json(
            self.store.job_dir(job["job_id"]) / "result.json",
            {"exit_code": 0, "finished_at": "2026-08-15T00:00:00Z"},
        )

        event_payload = mcp_server.wait_event(job["job_id"])
        event = json.loads(event_payload)
        ack = json.loads(mcp_server.ack_event(job["job_id"], event["event_id"]))

        self.assertLessEqual(len(event_payload.encode("utf-8")), 8192)
        self.assertEqual("completed", event["event_type"])
        self.assertTrue(ack["acknowledged"])

    def test_wait_any_tool_returns_original_event(self):
        first = self.store.start_job(name="first", cwd=self.cwd, command=["/bin/true"])
        second = self.store.start_job(name="second", cwd=self.cwd, command=["/bin/true"])
        self.store._atomic_write_json(self.store.job_dir(second["job_id"]) / "result.json", {"exit_code": 0})
        reply = mcp_server.StdioMcpServer()._tool_call("wait_any", {"job_ids": [first["job_id"], second["job_id"]]}, None)
        event = reply["structuredContent"]
        self.assertEqual(second["job_id"], event["job_id"])
        self.assertEqual("completed", event["event_type"])
        self.assertEqual(event["event_id"], self.store.inspect_job(second["job_id"])["pending_event"]["event_id"])


class McpStdioProtocolTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        env = os.environ.copy()
        env["PLJS_STATE_ROOT"] = str(Path(self.tmp.name) / "state")
        env["PLJS_POLL_INTERVAL_SECONDS"] = "0.05"
        self._responses = {}
        self.process = subprocess.Popen(
            [sys.executable, str(SCRIPTS / "mcp_server.py")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=env,
        )
        self.responses = queue.Queue()
        self.reader = threading.Thread(target=self._read_responses, daemon=True)
        self.reader.start()

    def _read_responses(self):
        for line in self.process.stdout:
            self.responses.put(json.loads(line))

    def tearDown(self):
        if self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=5)
        for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
            stream.close()
        self.tmp.cleanup()

    def request(self, request_id, method, params=None):
        message = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params is not None:
            message["params"] = params
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()
        return self.receive(request_id)

    def receive(self, request_id):
        deadline = time.monotonic() + 5
        while request_id not in self._responses:
            try:
                response = self.responses.get(timeout=max(0, deadline - time.monotonic()))
            except queue.Empty:
                detail = self.process.stderr.read() if self.process.poll() is not None else "MCP response timeout"
                self.fail(detail)
            self._responses[response.get("id")] = response
        return self._responses.pop(request_id)

    def test_initialize_list_and_call(self):
        initialized = self.request(
            1,
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1"},
            },
        )
        tools = self.request(2, "tools/list")
        listing = self.request(3, "tools/call", {"name": "list_jobs", "arguments": {}})

        self.assertEqual("2025-06-18", initialized["result"]["protocolVersion"])
        self.assertEqual(set(mcp_server.TOOL_NAMES), {tool["name"] for tool in tools["result"]["tools"]})
        self.assertEqual([], listing["result"]["structuredContent"]["jobs"])
        self.assertFalse(listing["result"]["isError"])

    def test_receives_concurrent_responses_in_requested_order(self):
        for request_id in (20, 21):
            self.process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": request_id, "method": "ping"}) + "\n")
        self.process.stdin.flush()

        self.assertEqual({}, self.receive(21)["result"])
        self.assertEqual({}, self.receive(20)["result"])

    def make_wait_job(self):
        job_dir = Path(self.tmp.name) / "state" / "jobs" / "20260815000000-canceltest00"
        job_dir.mkdir(parents=True)
        registration = {
            "schema_version": 2,
            "job_id": job_dir.name,
            "name": "cancel",
            "cwd": self.tmp.name,
            "process": require_process_identity(os.getpid()),
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "executable": "true",
            "argument_count": 1,
            "heartbeat_path": None,
            "stale_after_seconds": None,
            "artifacts": [],
            "python_executable": sys.executable,
            "supervisor_path": str(SCRIPTS / "supervisor.py"),
            "paths": {
                "job_dir": str(job_dir),
                "log": str(job_dir / "combined.log"),
                "result": str(job_dir / "result.json"),
            },
        }
        (job_dir / "job.json").write_text(json.dumps(registration))
        (job_dir / "events.json").write_text(json.dumps({"schema_version": 2, "next_event_id": 1, "events": [], "conditions": {}}))
        (job_dir / "combined.log").touch()
        return job_dir

    def start_wait(self, job_dir, tool="wait_event"):
        wait_request = {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {"name": tool, "arguments": {"job_ids": [job_dir.name]} if tool == "wait_any" else {"job_id": job_dir.name}},
        }
        self.process.stdin.write(json.dumps(wait_request) + "\n")
        self.process.stdin.flush()

    def assert_job_unchanged(self, job_dir):
        self.assertIsNone(self.process.poll())
        self.assertFalse((job_dir / "result.json").exists())
        self.assertEqual([], json.loads((job_dir / "events.json").read_text())["events"])
        observed = self.request(12, "tools/call", {"name": "inspect_job", "arguments": {"job_id": job_dir.name}})
        self.assertTrue(observed["result"]["structuredContent"]["process_state"]["active"])

    def test_cancelled_wait_returns_and_preserves_job(self):
        job_dir = self.make_wait_job()
        self.start_wait(job_dir)
        self.process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 10}}) + "\n")
        self.process.stdin.flush()
        response = self.receive(10)
        self.assertTrue(response["result"]["isError"])
        self.assertIn("wait cancelled", response["result"]["content"][0]["text"])
        self.assert_job_unchanged(job_dir)
        self.assertEqual({}, self.request(11, "ping")["result"])

    def test_cross_process_interrupt_releases_multi_wait(self):
        job_dir = self.make_wait_job()
        self.start_wait(job_dir, "wait_any")
        # Observe that this request is reading durable state before interrupting.
        # A protocol ping alone would not establish that the wait has started.
        deadline = time.monotonic() + 5
        while not (job_dir / "events.lock").exists():
            self.assertLess(time.monotonic(), deadline)
            time.sleep(0.01)
        interrupted = subprocess.run(
            [sys.executable, str(SCRIPTS / "supervisor.py"), "--state-root", str(job_dir.parents[1]), "interrupt-wait", job_dir.name],
            capture_output=True, text=True, timeout=5,
        )
        self.assertEqual(0, interrupted.returncode, interrupted.stderr)
        self.assertTrue(json.loads(interrupted.stdout)["underlying_job_unchanged"])
        response = self.receive(10)
        self.assertTrue(response["result"]["isError"])
        self.assertIn("wait interrupted", response["result"]["content"][0]["text"])
        self.assert_job_unchanged(job_dir)


if __name__ == "__main__":
    unittest.main()
