import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from durable import atomic_write_json  # noqa: E402
from monitoring import (  # noqa: E402
    MonitorEngine,
    MonitorError,
    NvidiaAdapter,
    discover_capabilities,
    normalize_monitors,
)


class FakeNvidia:
    def __init__(self):
        self.observed = {0: 0.0, 1: 40.0}
        self.error = None

    def devices(self):
        return [
            {"index": 0, "uuid": "GPU-aaa", "name": "A"},
            {"index": 1, "uuid": "GPU-bbb", "name": "B"},
        ]

    def process_sample(self, target_pids):
        del target_pids
        if self.error:
            raise MonitorError(self.error)
        return dict(self.observed)


class MonitorConfigTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = Path(self.tmp.name)
        self.adapter = FakeNvidia()

    def tearDown(self):
        self.tmp.cleanup()

    @mock.patch("monitoring.linux_process_tree_available", return_value=True)
    def test_gpu_index_normalizes_to_stable_uuid(self, _available):
        monitors = normalize_monitors(
            [
                {
                    "kind": "gpu_process_idle",
                    "devices": [1, "GPU-aaa"],
                    "utilization_below_percent": 5,
                    "duration_seconds": 900,
                    "startup_grace_seconds": 300,
                }
            ],
            self.cwd,
            self.adapter,
        )
        self.assertEqual(["GPU-bbb", "GPU-aaa"], [item["uuid"] for item in monitors[0]["devices"]])
        self.assertEqual(10.0, monitors[0]["sample_interval_seconds"])

    def test_strict_schema_rejects_unknown_duplicate_and_missing_disk_threshold(self):
        base = {
            "kind": "heartbeat_stale",
            "path": "beat",
            "stale_after_seconds": 10,
        }
        with self.assertRaisesRegex(MonitorError, "unknown monitor fields"):
            normalize_monitors([{**base, "command": "arbitrary"}], self.cwd, self.adapter)
        with self.assertRaisesRegex(MonitorError, "duplicate monitor kind"):
            normalize_monitors([base, base], self.cwd, self.adapter)
        with self.assertRaisesRegex(MonitorError, "requires an absolute or percentage"):
            normalize_monitors(
                [{"kind": "disk_free", "paths": [str(self.cwd)], "duration_seconds": 60}],
                self.cwd,
                self.adapter,
            )

    def test_disk_monitor_accepts_a_future_output_path_on_an_existing_filesystem(self):
        future = self.cwd / "not-created" / "output"
        monitors = normalize_monitors(
            [
                {
                    "kind": "disk_free",
                    "paths": [str(future)],
                    "available_below_gib": 20,
                    "duration_seconds": 60,
                }
            ],
            self.cwd,
            self.adapter,
        )
        self.assertEqual(str(future), monitors[0]["paths"][0])

    @mock.patch("monitoring._run")
    def test_nvidia_process_sample_excludes_unrelated_pids(self, run):
        run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="# gpu pid type sm mem enc dec command\n0 101 C 7 0 0 0 python\n0 999 C 83 0 0 0 other\n1 102 C 4 0 0 0 python\n",
            stderr="",
        )
        observed = NvidiaAdapter("/usr/bin/nvidia-smi").process_sample({101, 102})
        self.assertEqual({0: 7.0, 1: 4.0}, observed)

    @mock.patch("monitoring.linux_process_tree_available", return_value=True)
    def test_capabilities_report_process_attribution_and_devices(self, _available):
        capabilities = discover_capabilities(self.adapter)
        gpu = capabilities["monitors"]["gpu_process_idle"]
        self.assertTrue(gpu["available"])
        self.assertTrue(gpu["process_attribution"])
        self.assertEqual("GPU-aaa", gpu["devices"][0]["uuid"])

    @mock.patch("monitoring.linux_process_tree_available", return_value=False)
    @mock.patch("monitoring.sys.platform", "darwin")
    def test_macos_capabilities_keep_posix_monitors_without_gpu(self, _available):
        capabilities = discover_capabilities(self.adapter)

        self.assertEqual("darwin", capabilities["platform"])
        self.assertFalse(capabilities["monitors"]["gpu_process_idle"]["available"])
        self.assertTrue(capabilities["monitors"]["disk_free"]["available"])
        self.assertTrue(capabilities["monitors"]["heartbeat_stale"]["available"])

    @mock.patch("monitoring.linux_process_tree_available", return_value=False)
    @mock.patch("monitoring.sys.platform", "win32")
    def test_windows_capabilities_keep_filesystem_monitors_without_gpu(self, _available):
        capabilities = discover_capabilities(self.adapter)

        self.assertEqual("windows", capabilities["platform"])
        self.assertFalse(capabilities["monitors"]["gpu_process_idle"]["available"])
        self.assertTrue(capabilities["monitors"]["disk_free"]["available"])
        self.assertTrue(capabilities["monitors"]["heartbeat_stale"]["available"])


class MonitorEngineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.job_dir = Path(self.tmp.name)
        self.registration = {
            "job_id": "20260817000000-monitor00001",
            "created_epoch": 0,
            "monitors": [],
        }
        atomic_write_json(
            self.job_dir / "events.json",
            {"schema_version": 3, "next_event_id": 1, "events": [], "monitor_states": {}},
        )
        self.adapter = FakeNvidia()

    def tearDown(self):
        self.tmp.cleanup()

    def events(self):
        return json.loads((self.job_dir / "events.json").read_text(encoding="utf-8"))["events"]

    @mock.patch("monitoring.process_tree", return_value={123, 124})
    def test_any_gpu_uses_independent_episode_timers_and_rearms(self, tree):
        del tree
        self.registration["monitors"] = [
            {
                "monitor_id": "m1",
                "kind": "gpu_process_idle",
                "devices": self.adapter.devices(),
                "mode": "any",
                "utilization_below_percent": 5.0,
                "duration_seconds": 1.0,
                "startup_grace_seconds": 0.0,
                "sample_interval_seconds": 0.1,
            }
        ]
        engine = MonitorEngine(self.job_dir, self.registration, 123, self.adapter)
        engine.tick(100)
        engine.tick(101.1)
        first = self.events()
        self.assertEqual(1, len(first))
        self.assertEqual("GPU-aaa", first[0]["subject"])
        self.assertEqual("job_process_tree", first[0]["scope"])

        self.adapter.observed[0] = 20.0
        engine.tick(102)
        self.adapter.observed[0] = 0.0
        engine.tick(103)
        engine.tick(104.1)
        self.assertEqual(2, len(self.events()))

    @mock.patch("monitoring.process_tree", return_value={123})
    def test_probe_error_is_sustained_and_does_not_become_terminal(self, tree):
        del tree
        self.registration["monitors"] = [
            {
                "monitor_id": "m1",
                "kind": "gpu_process_idle",
                "devices": [self.adapter.devices()[0]],
                "mode": "any",
                "utilization_below_percent": 5.0,
                "duration_seconds": 1.0,
                "startup_grace_seconds": 0.0,
                "sample_interval_seconds": 1.0,
            }
        ]
        self.adapter.error = "driver query unavailable"
        engine = MonitorEngine(self.job_dir, self.registration, 123, self.adapter)
        engine.tick(100)
        engine.tick(131)
        self.assertEqual("gpu_probe_error", self.events()[0]["reason"])
        self.assertEqual("driver query unavailable", self.events()[0]["evidence_gap"])

    def test_disk_and_heartbeat_are_filesystem_and_declared_path_scoped(self):
        heartbeat = self.job_dir / "heartbeat"
        heartbeat.touch()
        os.utime(heartbeat, (1, 1))
        self.registration["monitors"] = [
            {
                "monitor_id": "m1",
                "kind": "disk_free",
                "paths": [str(self.job_dir), str(self.job_dir)],
                "available_below_gib": 10**9,
                "duration_seconds": 1.0,
                "sample_interval_seconds": 0.1,
            },
            {
                "monitor_id": "m2",
                "kind": "heartbeat_stale",
                "path": str(heartbeat),
                "stale_after_seconds": 1.0,
                "startup_grace_seconds": 0.0,
                "sample_interval_seconds": 0.1,
            },
        ]
        engine = MonitorEngine(self.job_dir, self.registration, 123, self.adapter)
        engine.tick(100)
        engine.tick(101.1)
        events = self.events()
        self.assertEqual(2, len(events))
        self.assertEqual({"filesystem", "job_declared_path"}, {event["scope"] for event in events})
        self.assertEqual(1, sum(event["reason"] == "disk_free_low" for event in events))


if __name__ == "__main__":
    unittest.main()
