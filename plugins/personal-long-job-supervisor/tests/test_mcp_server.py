import json
import os
from datetime import datetime, timezone
from pathlib import Path
import selectors
import subprocess
import sys
import tempfile
import time
import unittest


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import mcp_server  # noqa: E402
from supervisor import JobStore  # noqa: E402


class FakeSystemd:
    def start(self, registration, worker_path, python_executable):
        return None

    def inspect(self, unit):
        return {"ActiveState": "active", "SubState": "running", "Result": "success"}


class McpObservationContractTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = JobStore(Path(self.tmp.name) / "state", systemd=FakeSystemd())
        self.cwd = Path(self.tmp.name) / "work"
        self.cwd.mkdir()
        mcp_server.STORE = self.store

    def tearDown(self):
        self.tmp.cleanup()

    def test_exposes_only_observation_and_ack_tools(self):
        self.assertEqual(
            {"wait_event", "inspect_job", "list_jobs", "ack_event"},
            set(mcp_server.TOOL_NAMES),
        )

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


class McpStdioProtocolTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        env = os.environ.copy()
        env["PLJS_STATE_ROOT"] = str(Path(self.tmp.name) / "state")
        env["PLJS_POLL_INTERVAL_SECONDS"] = "0.05"
        self.process = subprocess.Popen(
            [sys.executable, str(SCRIPTS / "mcp_server.py")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=env,
        )

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
        deadline = time.time() + 5
        selector = selectors.DefaultSelector()
        selector.register(self.process.stdout, selectors.EVENT_READ)
        try:
            while time.time() < deadline:
                ready = selector.select(timeout=max(0, deadline - time.time()))
                self.assertTrue(ready, self.process.stderr.read() if self.process.poll() is not None else "MCP response timeout")
                response = json.loads(self.process.stdout.readline())
                if response.get("id") == request_id:
                    return response
            self.fail("MCP response timeout")
        finally:
            selector.close()

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

    def test_cancelled_wait_does_not_stop_server(self):
        job_dir = Path(self.tmp.name) / "state" / "jobs" / "20260815000000-canceltest00"
        job_dir.mkdir(parents=True)
        registration = {
            "schema_version": 1,
            "job_id": job_dir.name,
            "name": "cancel",
            "cwd": self.tmp.name,
            "unit": "not-running.service",
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
        (job_dir / "events.json").write_text(json.dumps({"schema_version": 1, "next_event_id": 1, "events": [], "conditions": {}}))
        (job_dir / "combined.log").touch()
        wait_request = {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {"name": "wait_event", "arguments": {"job_id": job_dir.name}},
        }
        self.process.stdin.write(json.dumps(wait_request) + "\n")
        self.process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 10}}) + "\n")
        self.process.stdin.flush()

        response = self.request(11, "ping")
        self.assertEqual({}, response["result"])


if __name__ == "__main__":
    unittest.main()
