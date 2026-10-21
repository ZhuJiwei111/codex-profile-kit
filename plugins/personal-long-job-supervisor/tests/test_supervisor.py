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

from supervisor import (  # noqa: E402
    DetachedProcessRuntime,
    JobStore,
    SupervisorError,
)


class FakeRuntime:
    def __init__(self):
        self.started = []
        self.states = {}
        self.next_pid = 1000

    def start(self, registration, worker_path, python_executable):
        self.started.append((registration, worker_path, python_executable))
        identity = {"pid": self.next_pid, "start_ticks": self.next_pid * 10}
        self.next_pid += 1
        self.states[identity["pid"]] = {
            **identity,
            "observed_start_ticks": identity["start_ticks"],
            "identity_matches": True,
            "active": True,
            "state": "running",
        }
        return identity

    def inspect(self, process):
        return self.states.get(
            process["pid"],
            {
                **process,
                "observed_start_ticks": None,
                "identity_matches": False,
                "active": False,
                "state": "exited",
            },
        )


class JobStoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "state"
        self.runtime = FakeRuntime()
        self.store = JobStore(self.root, runtime=self.runtime)
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
        self.assertEqual(1, len(self.runtime.started))
        self.assertGreater(registration["process"]["pid"], 0)
        self.assertGreater(registration["process"]["start_ticks"], 0)

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
        restarted = JobStore(self.root, runtime=self.runtime)
        observed = restarted.inspect_job(job["job_id"])

        self.assertTrue(first["acknowledged"])
        self.assertTrue(second["already_acknowledged"])
        self.assertIsNone(observed["pending_event"])
        self.assertEqual("completed", observed["status"])
        with self.assertRaisesRegex(SupervisorError, "already terminal"):
            restarted.wait_event(job["job_id"], poll_interval=0.001)

    def test_consumed_supervisor_error_does_not_wait_forever(self):
        job = self.start()
        path = self.store.job_dir(job["job_id"]) / "job.json"
        registration = json.loads(path.read_text())
        registration["created_at"] = "2020-01-01T00:00:00Z"
        self.store._atomic_write_json(path, registration)
        self.runtime.states.clear()
        event = self.store.wait_event(job["job_id"])
        self.assertEqual("supervisor_error", event["event_type"])
        self.store.ack_event(job["job_id"], event["event_id"])
        self.assertFalse(self.store.inspect_job(job["job_id"])["waitable"])
        # Keep the regression bounded even if the wait closure regresses.
        cancel = threading.Event()
        timer = threading.Timer(0.5, cancel.set)
        timer.start()
        try:
            with self.assertRaisesRegex(SupervisorError, "already terminal or inactive"):
                self.store.wait_event(job["job_id"], poll_interval=0.01, cancel_event=cancel)
        finally:
            timer.cancel()
            timer.join()

    def test_wait_any_skips_closed_and_keeps_other_events_unacknowledged(self):
        closed, running, done = self.start(), self.start(), self.start()
        self.write_result(closed["job_id"], 0)
        event = self.store.wait_event(closed["job_id"])
        self.store.ack_event(closed["job_id"], event["event_id"])
        self.write_result(done["job_id"], 0)
        event = self.store.wait_any([closed["job_id"], running["job_id"], done["job_id"]])
        self.assertEqual(done["job_id"], event["job_id"])
        self.assertEqual(event["event_id"], self.store.inspect_job(done["job_id"])["pending_event"]["event_id"])
        self.assertTrue(self.store.inspect_job(running["job_id"])["process_state"]["active"])

    def test_interrupt_wait_cross_store_preserves_jobs_and_future_waits(self):
        first, second = self.start(), self.start()
        ready = threading.Event()
        errors = []
        original = self.store.inspect_job

        def inspect(job_id):
            ready.set()
            return original(job_id)

        def wait():
            try:
                self.store.wait_any([first["job_id"], second["job_id"]], poll_interval=0.01)
            except SupervisorError as error:
                errors.append(str(error))

        with mock.patch.object(self.store, "inspect_job", side_effect=inspect):
            thread = threading.Thread(target=wait, daemon=True)
            thread.start()
            self.assertTrue(ready.wait(1))
            other = JobStore(self.root, runtime=self.runtime)
            other.interrupt_wait(second["job_id"])
            thread.join(timeout=1)
        self.assertFalse(thread.is_alive())
        self.assertIn("wait interrupted", errors[0])
        for job in (first, second):
            observed = self.store.inspect_job(job["job_id"])
            self.assertTrue(observed["process_state"]["active"])
            self.assertIsNone(observed["pending_event"])
        self.write_result(second["job_id"], 0)
        event = other.wait_any([first["job_id"], second["job_id"]])
        self.assertEqual(second["job_id"], event["job_id"])

    def test_wait_any_rejects_empty_or_invalid_job_list(self):
        for value in ([], "job", [None]):
            with self.subTest(value=value), self.assertRaises(SupervisorError):
                self.store.wait_any(value)

    def test_restart_recovers_process_identity_written_by_worker(self):
        job = self.start()
        job_dir = self.store.job_dir(job["job_id"])
        registration_path = job_dir / "job.json"
        registration = json.loads(registration_path.read_text(encoding="utf-8"))
        process = registration.pop("process")
        self.store._atomic_write_json(registration_path, registration)
        self.store._atomic_write_json(job_dir / "process.json", process)

        restarted = JobStore(self.root, runtime=self.runtime)
        observed = restarted.inspect_job(job["job_id"])
        recovered = json.loads(registration_path.read_text(encoding="utf-8"))

        self.assertEqual(process, observed["process"])
        self.assertEqual(process, recovered["process"])

    def test_heartbeat_stale_attention_does_not_stop_or_repeat(self):
        heartbeat = self.cwd / "heartbeat"
        heartbeat.touch()
        old = time.time() - 100
        os.utime(heartbeat, (old, old))
        job = self.start()
        registration_path = self.store.job_dir(job["job_id"]) / "job.json"
        registration = json.loads(registration_path.read_text(encoding="utf-8"))
        registration.update(
            schema_version=2,
            heartbeat_path=str(heartbeat),
            stale_after_seconds=5,
        )
        self.store._atomic_write_json(registration_path, registration)

        event = self.store.wait_event(job["job_id"], poll_interval=0.001)
        self.assertEqual("attention", event["event_type"])
        self.assertTrue(self.runtime.inspect(job["process"])["active"])
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

    def test_clean_removes_only_an_inactive_registration(self):
        job = self.start()
        self.write_result(job["job_id"], 0)
        event = self.store.wait_event(job["job_id"], poll_interval=0.001)
        self.store.ack_event(job["job_id"], event["event_id"])
        self.runtime.states[job["process"]["pid"]] = {
            **job["process"],
            "observed_start_ticks": None,
            "identity_matches": False,
            "active": False,
            "state": "exited",
        }

        cleaned = self.store.clean_job(job["job_id"])

        self.assertTrue(cleaned["cleaned"])
        self.assertFalse(self.store.job_dir(job["job_id"]).exists())

    def test_clean_refuses_pid_disappearance_without_a_terminal_event(self):
        job = self.start()
        self.runtime.states[job["process"]["pid"]] = {
            **job["process"],
            "observed_start_ticks": None,
            "identity_matches": False,
            "active": False,
            "state": "exited",
        }

        with self.assertRaisesRegex(SupervisorError, "confirmed terminal event"):
            self.store.clean_job(job["job_id"])

        self.assertTrue(self.store.job_dir(job["job_id"]).exists())

    def test_pid_reuse_is_identity_loss_not_a_running_job(self):
        job = self.start()
        self.runtime.states[job["process"]["pid"]] = {
            **job["process"],
            "observed_start_ticks": job["process"]["start_ticks"] + 1,
            "identity_matches": False,
            "active": False,
            "state": "identity_lost",
        }
        registration_path = self.store.job_dir(job["job_id"]) / "job.json"
        registration = json.loads(registration_path.read_text(encoding="utf-8"))
        registration["created_at"] = "2026-08-15T00:00:00Z"
        self.store._atomic_write_json(registration_path, registration)

        observed = self.store.inspect_job(job["job_id"])

        self.assertEqual("identity_lost", observed["status"])
        self.assertFalse(observed["process_state"]["identity_matches"])
        self.assertEqual("supervisor_error", observed["pending_event"]["event_type"])
        self.assertIn("identity was lost", observed["pending_event"]["detail"])


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

    def test_start_help_exposes_repeatable_monitor_json(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPTS / "supervisor.py"), "start", "--help"],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("--monitor", completed.stdout)
        self.assertNotIn("--gpu-id", completed.stdout)

    @mock.patch.object(DetachedProcessRuntime, "_identity")
    @mock.patch("supervisor.subprocess.Popen")
    def test_detached_launch_starts_new_session(self, popen, identity):
        popen.return_value.pid = 1234
        popen.return_value.poll.return_value = None
        identity.return_value = {"pid": 1234, "start_ticks": 5678, "state_code": "R"}
        runtime = DetachedProcessRuntime()
        with tempfile.TemporaryDirectory() as temporary:
            job_dir = Path(temporary) / "job"
            job_dir.mkdir()
            log = job_dir / "combined.log"
            log.touch()
            identity_path = job_dir / "process.json"
            identity_path.write_text(
                json.dumps({"pid": 1234, "start_ticks": 5678}), encoding="utf-8"
            )
            registration = {
                "cwd": temporary,
                "paths": {
                    "job_dir": str(job_dir),
                    "log": str(log),
                    "identity": str(identity_path),
                },
                "_launch_command": ["/bin/true"],
            }

            observed = runtime.start(registration, Path("/worker.py"), sys.executable)

        self.assertEqual({"pid": 1234, "start_ticks": 5678}, observed)
        self.assertTrue(popen.call_args.kwargs["start_new_session"])
        self.assertEqual(subprocess.DEVNULL, popen.call_args.kwargs["stdin"])
        self.assertEqual(subprocess.STDOUT, popen.call_args.kwargs["stderr"])

    def test_launch_failure_reports_recoverable_job_id(self):
        runtime = FakeRuntime()
        runtime.start = mock.Mock(side_effect=SupervisorError("launcher unavailable"))
        with tempfile.TemporaryDirectory() as temporary:
            store = JobStore(Path(temporary) / "state", runtime=runtime)
            with self.assertRaisesRegex(SupervisorError, r"registered job \d{14}-[a-f0-9]{12}"):
                store.start_job(name="launch-fail", cwd=temporary, command=["/bin/true"])


if __name__ == "__main__":
    unittest.main()
