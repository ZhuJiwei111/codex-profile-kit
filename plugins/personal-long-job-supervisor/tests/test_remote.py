import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from durable import append_event, atomic_write_json, locked_events, read_json
from supervisor import JobStore, SupervisorError
from remote import RemoteClient, RoutedJobStore
from test_supervisor import FakeRuntime


class SharedConnectionsTest(unittest.TestCase):
    def test_shared_target_change_reaches_both_projects(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shared = root / "connections.json"
            config = {"default_target": "42", "targets": {"42": {"ssh_alias": "main"}},
                      "supervisor": {"entry": "/shared/remote.py", "python": "/usr/bin/python3"}}
            shared.write_text(json.dumps(config))
            for name in ["paper", "space"]:
                local = root / name / ".local"
                local.mkdir(parents=True)
                (local / "connections.json").symlink_to(shared)
                (local / "project.json").write_text(json.dumps({"worktree": "/"+name, "supervisor": {"state_root": name}}))
                client = RemoteClient(root / name)
                self.assertEqual(client.target, "42")
                self.assertEqual(client.config["supervisor"]["entry"], "/shared/remote.py")
                self.assertEqual(client.config["supervisor"]["state_root"], name)
            config.update(default_target="33", targets={"33": {"ssh_alias": "new"}})
            shared.write_text(json.dumps(config))
            for name in ["paper", "space"]:
                client = RemoteClient(root / name)
                self.assertEqual(client.target, "33")
                self.assertEqual(list(client.config["targets"]), ["33"])
                self.assertEqual(client.config["worktree"], "/"+name)
                self.assertEqual(client.config["supervisor"]["state_root"], name)


class RemoteCoreTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.runtime = FakeRuntime()
        self.store = JobStore(self.root / "state", runtime=self.runtime)
        self.args = dict(name="remote-test", cwd=str(self.root), command=["/bin/echo", "ok"],
                         request_id="remote-test-0001", event_lock="mkdir")
    def tearDown(self):
        self.temp.cleanup()

    def test_retry_attaches_and_payload_change_rejected(self):
        first = self.store.start_job(**self.args)
        second = self.store.start_job(**self.args)
        self.assertEqual(first["job_id"], second["job_id"])
        self.assertEqual(len(self.runtime.started), 1)
        with self.assertRaisesRegex(SupervisorError, "different launch"):
            self.store.start_job(**dict(self.args, command=["/bin/echo", "different"]))

    def test_partial_registration_never_relaunches(self):
        self.store.job_dir(self.args["request_id"]).mkdir()
        with self.assertRaisesRegex(SupervisorError, "launch unconfirmed"):
            self.store.start_job(**self.args)
        self.assertEqual(self.runtime.started, [])

    def test_spawn_gap_never_relaunches(self):
        first = self.store.start_job(**self.args)
        path = self.store.job_dir(first["job_id"]) / "job.json"
        row = read_json(path)
        row.pop("process")
        atomic_write_json(path, row)
        with self.assertRaisesRegex(SupervisorError, "not yet available"):
            self.store.start_job(**self.args)
        self.assertEqual(len(self.runtime.started), 1)

    def test_shared_result_recovery_never_inspects_foreign_pid(self):
        job = self.store.start_job(**self.args)
        path = self.store.job_dir(job["job_id"])
        row = read_json(path / "job.json")
        row["execution_host"] = {"different": "released instance"}
        atomic_write_json(path / "job.json", row)
        atomic_write_json(path / "result.json", {"exit_code": 0, "finished_at": "2026-11-19T00:00:00Z"})
        with mock.patch.object(self.runtime, "inspect", side_effect=AssertionError("foreign PID inspected")):
            recovered = self.store.inspect_job(job["job_id"])
        self.assertEqual(recovered["status"], "completed")
        self.assertEqual(recovered["process_state"]["state"], "execution_host_unverified")

    def test_shared_unfinished_job_is_not_declared_failed_or_restarted(self):
        job = self.store.start_job(**self.args)
        path = self.store.job_dir(job["job_id"]) / "job.json"
        row = read_json(path)
        row["execution_host"] = {"different": True}
        row["created_at"] = "2000-01-01T00:00:00Z"
        atomic_write_json(path, row)
        with mock.patch.object(self.runtime, "inspect", side_effect=AssertionError("foreign PID inspected")):
            result = self.store.inspect_job(job["job_id"])
        self.assertEqual(result["status"], "execution_host_unverified")
        self.assertIsNone(result["pending_event"])
        self.assertFalse(result["waitable"])
        self.assertEqual(len(self.runtime.started), 1)

    def test_directory_event_lock_preserves_concurrent_events(self):
        job = self.store.start_job(**self.args)
        directory = self.store.job_dir(job["job_id"])
        row = read_json(directory / "job.json")
        errors = []
        def add():
            try:
                with locked_events(directory) as events:
                    append_event(events, row, "attention", reason="fixture")
            except Exception as error:
                errors.append(error)
        threads = [threading.Thread(target=add) for _ in range(12)]
        for thread in threads: thread.start()
        for thread in threads: thread.join()
        self.assertFalse(errors)
        self.assertEqual(len(read_json(directory / "events.json")["events"]), 12)

    def test_cleaned_request_cannot_be_replayed(self):
        job = self.store.start_job(**self.args)
        directory = self.store.job_dir(job["job_id"])
        atomic_write_json(directory / "result.json", {"exit_code": 0, "finished_at": "2026-11-19T00:00:00Z"})
        self.runtime.states[job["process"]["pid"]]["active"] = False
        event = self.store.inspect_job(job["job_id"])["pending_event"]
        self.store.ack_event(job["job_id"], event["event_id"])
        self.store.clean_job(job["job_id"])
        with self.assertRaisesRegex(SupervisorError, "already cleaned"):
            self.store.start_job(**self.args)
        self.assertEqual(len(self.runtime.started), 1)


class LocatorTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        (self.project / ".local").mkdir(parents=True)
        self.config = {"worktree": "/shared/project", "default_target": "a",
            "targets": {"a": {"ssh_alias": "alias-a"}, "b": {"ssh_alias": "alias-b"}},
            "supervisor": {"python": "/python", "entry": "/plugin/remote.py", "state_root": "/shared/state"}}
        atomic_write_json(self.project / ".local/connections.json", self.config)
        self.env = mock.patch.dict(os.environ, {"PLJS_STATE_ROOT": str(self.root / "controller")})
        self.env.start()
    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def test_locator_exists_before_uncertain_launch_and_mcp_routes_by_id(self):
        client = RemoteClient(self.project)
        def fail(*args, **kwargs):
            self.assertTrue(client.locator_path("remote-fixture-01").exists())
            raise SupervisorError("connection lost")
        with mock.patch.object(client, "rpc", side_effect=fail):
            with self.assertRaisesRegex(SupervisorError, "job_id=remote-fixture-01"):
                client.start_job(request_id="remote-fixture-01", name="test", cwd="/shared/project", command=["/bin/true"])
        self.config["default_target"] = "b"
        atomic_write_json(self.project / ".local/connections.json", self.config)
        with mock.patch.object(RemoteClient, "rpc", return_value={"status": "running"}) as rpc:
            result = RoutedJobStore().inspect_job("remote-fixture-01")
        self.assertEqual(result["status"], "running")
        self.assertEqual(rpc.call_args.kwargs["target"], "a")

    def test_start_rejects_recovery_route(self):
        with self.assertRaisesRegex(SupervisorError, "--via"):
            RemoteClient(self.project, via="b").start_job(name="x", cwd="/shared", command=["/bin/true"])

    def test_recovery_preserves_registered_read_route(self):
        client = RemoteClient(self.project)
        client.reserve("remote-fixture-03", "a", "/shared/state")
        new = RemoteClient(self.project, target="b")
        with mock.patch.object(new, "rpc", return_value={"jobs": [{"job_id": "remote-fixture-03"}]}):
            new.recover()
        self.assertEqual(new.locator("remote-fixture-03")["target"], "a")

    def test_remote_wait_keeps_interrupt_token_across_ssh_requests(self):
        client = RemoteClient(self.project)
        client.reserve("remote-fixture-04", "a", "/shared/state")
        with mock.patch.object(client, "rpc", side_effect=[
            {"idle": True, "wait_tokens": {"remote-fixture-04": "before-interrupt"}},
            SupervisorError("wait interrupted")]) as rpc:
            with self.assertRaisesRegex(SupervisorError, "interrupted"):
                client.wait_any(["remote-fixture-04"])
        self.assertEqual(rpc.call_args.kwargs["wait_tokens"], {"remote-fixture-04": "before-interrupt"})

    def test_mixed_remote_groups_return_event_without_waiting_for_other_target(self):
        client = RemoteClient(self.project)
        client.reserve("remote-fixture-05", "a", "/shared/state")
        client.reserve("remote-fixture-06", "b", "/shared/state")
        def waiting(self, ids, **kwargs):
            if ids == ["remote-fixture-05"]:
                return {"job_id": ids[0], "event_id": 1}
            cancel = kwargs["cancel_event"]
            while not cancel.is_set():
                cancel.wait(0.01)
            raise SupervisorError("wait cancelled")
        with mock.patch.object(RemoteClient, "wait_any", waiting):
            result = RoutedJobStore().wait_any(["remote-fixture-05", "remote-fixture-06"])
        self.assertEqual(result["job_id"], "remote-fixture-05")

    def test_recovery_rebuilds_disposable_controller_index(self):
        client = RemoteClient(self.project, target="b")
        with mock.patch.object(client, "rpc", return_value={"jobs": [{"job_id": "remote-fixture-02", "terminal": True}]}):
            result = client.recover()
        self.assertEqual(result["recovered"], ["remote-fixture-02"])
        self.assertEqual(client.locator("remote-fixture-02")["target"], "b")


if __name__ == "__main__":
    unittest.main()
