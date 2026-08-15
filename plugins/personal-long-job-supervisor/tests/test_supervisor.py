import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from supervisor import JobStore, SupervisorError, SystemdUser  # noqa: E402


class FakeSystemd:
    def __init__(self):
        self.started = []
        self.states = {}
        self.cleaned = []

    def start(self, registration, worker_path, python_executable):
        self.started.append((registration, worker_path, python_executable))
        self.states[registration["unit"]] = {
            "ActiveState": "active",
            "SubState": "running",
            "Result": "success",
            "ExecMainStatus": "0",
        }

    def inspect(self, unit):
        return self.states.get(
            unit,
            {
                "ActiveState": "inactive",
                "SubState": "dead",
                "Result": "success",
                "ExecMainStatus": "0",
            },
        )

    def clean(self, unit):
        self.cleaned.append(unit)
        self.states.pop(unit, None)


class JobStoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "state"
        self.systemd = FakeSystemd()
        self.store = JobStore(self.root, systemd=self.systemd)
        self.cwd = Path(self.tmp.name) / "work"
        self.cwd.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def start(self, **kwargs):
        return self.store.start_job(
            name=kwargs.pop("name", "sentinel"),
            cwd=self.cwd,
            command=kwargs.pop("command", ["/bin/sh", "-c", "exit 0"]),
            **kwargs,
        )

    def write_result(self, job_id, exit_code):
        self.store._atomic_write_json(
            self.store.job_dir(job_id) / "result.json",
            {"exit_code": exit_code, "finished_at": "2026-08-15T00:00:00Z"},
        )

    def test_start_registration_is_private_and_does_not_store_command(self):
        job = self.start(command=["/bin/echo", "secret-not-recorded"])
        job_dir = self.store.job_dir(job["job_id"])
        registration = json.loads((job_dir / "job.json").read_text())

        self.assertEqual(0o700, job_dir.stat().st_mode & 0o777)
        self.assertNotIn("command", registration)
        self.assertEqual("echo", registration["executable"])
        self.assertEqual(2, registration["argument_count"])
        self.assertEqual(1, len(self.systemd.started))

    def test_completed_and_failed_events_are_deduplicated(self):
        ok = self.start(name="ok")
        bad = self.start(name="bad")
        self.write_result(ok["job_id"], 0)
        self.write_result(bad["job_id"], 17)

        first_ok = self.store.inspect_job(ok["job_id"])
        second_ok = self.store.inspect_job(ok["job_id"])
        first_bad = self.store.inspect_job(bad["job_id"])

        self.assertEqual("completed", first_ok["pending_event"]["event_type"])
        self.assertEqual(first_ok["pending_event"]["event_id"], second_ok["pending_event"]["event_id"])
        self.assertEqual("failed", first_bad["pending_event"]["event_type"])
        self.assertEqual(17, first_bad["pending_event"]["exit_code"])

    def test_ack_is_idempotent_and_restart_reconciles_disk(self):
        job = self.start()
        self.write_result(job["job_id"], 0)
        event = self.store.wait_event(job["job_id"], poll_interval=0.001)

        first = self.store.ack_event(job["job_id"], event["event_id"])
        second = self.store.ack_event(job["job_id"], event["event_id"])
        restarted = JobStore(self.root, systemd=self.systemd)
        observed = restarted.inspect_job(job["job_id"])

        self.assertTrue(first["acknowledged"])
        self.assertTrue(second["already_acknowledged"])
        self.assertIsNone(observed["pending_event"])
        self.assertEqual("completed", observed["status"])
        with self.assertRaisesRegex(SupervisorError, "already terminal"):
            restarted.wait_event(job["job_id"], poll_interval=0.001)

    def test_heartbeat_stale_attention_does_not_stop_or_repeat(self):
        heartbeat = self.cwd / "heartbeat"
        heartbeat.touch()
        old = time.time() - 100
        os.utime(heartbeat, (old, old))
        job = self.start(heartbeat_path=heartbeat, stale_after=5)

        event = self.store.wait_event(job["job_id"], poll_interval=0.001)
        self.assertEqual("attention", event["event_type"])
        self.assertEqual("active", self.systemd.inspect(job["unit"])["ActiveState"])
        self.store.ack_event(job["job_id"], event["event_id"])
        self.assertIsNone(self.store.inspect_job(job["job_id"])["pending_event"])

        heartbeat.touch()
        self.store.inspect_job(job["job_id"])
        os.utime(heartbeat, (old, old))
        repeated = self.store.inspect_job(job["job_id"])["pending_event"]
        self.assertEqual("attention", repeated["event_type"])
        self.assertGreater(repeated["event_id"], event["event_id"])

    def test_concurrent_reconcile_has_one_terminal_event(self):
        job = self.start()
        self.write_result(job["job_id"], 0)
        results = []

        def inspect():
            results.append(self.store.inspect_job(job["job_id"])["pending_event"]["event_id"])

        threads = [threading.Thread(target=inspect) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(1, len(set(results)))

    def test_event_payload_is_bounded_and_does_not_contain_log_contents(self):
        artifacts = [self.cwd / ("artifact-" + "x" * 500 + str(i)) for i in range(40)]
        job = self.start(artifacts=artifacts)
        log_marker = "DO-NOT-INJECT-" + "z" * 20_000
        (self.store.job_dir(job["job_id"]) / "combined.log").write_text(log_marker)
        self.write_result(job["job_id"], 0)

        payload = self.store.render_payload(self.store.wait_event(job["job_id"], poll_interval=0.001))

        self.assertLessEqual(len(payload.encode("utf-8")), 8192)
        self.assertNotIn("DO-NOT-INJECT", payload)

    def test_inspect_payload_is_bounded_with_long_artifact_paths(self):
        artifacts = [self.cwd / ("artifact-" + "x" * 500 + str(i)) for i in range(40)]
        job = self.start(artifacts=artifacts)

        payload = self.store.render_payload(self.store.inspect_job(job["job_id"]))

        self.assertLessEqual(len(payload.encode("utf-8")), 8192)

    def test_list_payload_is_bounded_with_many_jobs(self):
        artifacts = [self.cwd / ("artifact-" + "x" * 200 + str(index)) for index in range(20)]
        for index in range(30):
            self.start(name=f"job-{index}", artifacts=artifacts)

        payload = self.store.render_payload(self.store.list_jobs())

        self.assertLessEqual(len(payload.encode("utf-8")), 8192)
        self.assertGreater(len(json.loads(payload)["jobs"]), 0)

    def test_corrupt_registration_fails_open_for_list_and_raises_for_exact_job(self):
        broken = self.root / "jobs" / "broken"
        broken.mkdir(parents=True)
        (broken / "job.json").write_text("not-json")

        listing = self.store.list_jobs()
        self.assertEqual([], listing["jobs"])
        self.assertEqual(1, listing["skipped_corrupt"])
        with self.assertRaises(SupervisorError):
            self.store.inspect_job("broken")

    def test_clean_resets_exact_inactive_unit(self):
        job = self.start()
        self.write_result(job["job_id"], 0)
        event = self.store.wait_event(job["job_id"], poll_interval=0.001)
        self.store.ack_event(job["job_id"], event["event_id"])
        self.systemd.states[job["unit"]] = {
            "LoadState": "loaded",
            "ActiveState": "inactive",
            "SubState": "dead",
            "Result": "success",
        }

        cleaned = self.store.clean_job(job["job_id"])

        self.assertTrue(cleaned["cleaned"])
        self.assertEqual([job["unit"]], self.systemd.cleaned)
        self.assertFalse(self.store.job_dir(job["job_id"]).exists())


class CliContractTest(unittest.TestCase):
    def test_cli_help_exposes_only_planned_lifecycle_commands(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPTS / "supervisor.py"), "--help"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        for command in ("start", "status", "list", "ack", "clean"):
            self.assertIn(command, completed.stdout)
        for forbidden in ("cancel", "retry", "restart"):
            self.assertNotIn(forbidden, completed.stdout)

    @mock.patch("supervisor.subprocess.run")
    def test_systemd_inspect_supplies_user_bus_environment(self, run):
        run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="ActiveState=active\nSubState=running\n", stderr=""
        )

        with mock.patch.dict(os.environ, {}, clear=True):
            observed = SystemdUser().inspect("example.service")

        environment = run.call_args.kwargs["env"]
        runtime = f"/run/user/{os.getuid()}"
        self.assertEqual(runtime, environment["XDG_RUNTIME_DIR"])
        self.assertEqual(f"unix:path={runtime}/bus", environment["DBUS_SESSION_BUS_ADDRESS"])
        self.assertEqual("active", observed["ActiveState"])

    def test_launch_failure_reports_recoverable_job_id(self):
        systemd = FakeSystemd()
        systemd.start = mock.Mock(side_effect=SupervisorError("launcher unavailable"))
        with tempfile.TemporaryDirectory() as temporary:
            store = JobStore(Path(temporary) / "state", systemd=systemd)
            with self.assertRaisesRegex(SupervisorError, r"registered job \d{14}-[a-f0-9]{12}"):
                store.start_job(name="launch-fail", cwd=temporary, command=["/bin/true"])


if __name__ == "__main__":
    unittest.main()
