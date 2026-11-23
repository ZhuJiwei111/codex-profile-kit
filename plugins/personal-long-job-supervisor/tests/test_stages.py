import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from durable import atomic_write_json, read_json
from stages import StageObserver
from supervisor import JobStore, SupervisorError
from test_supervisor import FakeRuntime


class StageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.runtime = FakeRuntime()
        self.store = JobStore(self.root / 'state', runtime=self.runtime)
        self.args = dict(name='stages', cwd=self.root, command=['/bin/echo', 'ok'],
                         request_id='stages-fixture', stage_path='stage.json')
        self.job = self.store.start_job(**self.args)
        self.job_id = self.job['job_id']
        self.directory = self.store.job_dir(self.job_id)
        self.observer = StageObserver(self.directory, read_json(self.directory / 'job.json'))

    def tearDown(self):
        self.tmp.cleanup()

    def publish(self, seq, stage='generation', **extra):
        atomic_write_json(self.root / 'stage.json', dict(job_id=self.job_id, seq=seq, stage=stage, **extra))
        self.observer.tick()

    def events(self):
        return read_json(self.directory / 'events.json')['events']

    def test_first_change_duplicate_and_return_to_earlier_stage(self):
        self.publish(0)
        self.publish(0)
        self.publish(1, 'scoring')
        self.publish(2, 'generation')
        self.assertEqual([e['stage']['stage'] for e in self.events()], ['generation', 'scoring', 'generation'])
        self.assertTrue(self.store.inspect_job(self.job_id)['waitable'])

    def test_bad_missing_old_job_and_stale_sequence_are_not_events(self):
        self.observer.tick()
        self.publish(4)
        self.publish(3)
        self.publish(4, 'changed-without-seq')
        atomic_write_json(self.root / 'stage.json', dict(job_id='other-job', seq=99, stage='done'))
        self.observer.tick()
        (self.root / 'stage.json').write_text('{broken')
        self.observer.tick()
        self.assertEqual(len(self.events()), 1)
        state = self.store.inspect_job(self.job_id)['stage_state']
        self.assertEqual(state['snapshot']['seq'], 4)
        self.assertTrue(state['evidence_gap'])
        self.publish(5, 'scoring')
        self.assertIsNone(self.store.inspect_job(self.job_id)['stage_state']['evidence_gap'])

    def test_retry_binding_and_reconnect_with_terminal(self):
        self.publish(0, facts='generation accepted')
        self.store.start_job(**self.args)
        self.assertEqual(len(self.runtime.started), 1)
        with self.assertRaises(SupervisorError):
            self.store.start_job(**dict(self.args, stage_path='different.json'))
        atomic_write_json(self.directory / 'result.json', {'exit_code': 1, 'finished_at': '2026-11-20T00:00:00Z'})
        resumed = JobStore(self.store.state_root, runtime=self.runtime)
        event = resumed.wait_event(self.job_id, poll_interval=0.001)
        self.assertEqual(event['event_type'], 'stage_changed')
        self.assertEqual(event['stage']['seq'], 0)
        self.assertEqual(resumed.inspect_job(self.job_id)['status'], 'failed')
        self.assertEqual(resumed.list_jobs()['jobs'][0]['pending_event']['stage']['seq'], 0)
        resumed.ack_event(self.job_id, event['event_id'])
        self.assertEqual(resumed.wait_event(self.job_id, poll_interval=0.001)['event_type'], 'failed')

    def test_large_stage_survives_inspection_reconnect_and_ack(self):
        self.publish(0, '阶' * 160, facts='实' * 512, evidence='证' * 512)
        store = JobStore(self.store.state_root, runtime=self.runtime)
        view = json.loads(store.render_payload(store.inspect_job(self.job_id)))
        event = store.wait_event(self.job_id)
        self.assertEqual(view['pending_event']['event_id'], event['event_id'])
        self.assertEqual(event['stage']['evidence'], '证' * 512)
        store.ack_event(self.job_id, event['event_id'])
        self.assertIsNone(store.inspect_job(self.job_id)['pending_event'])

    def test_invalid_optional_fields_leave_sequence_available(self):
        self.publish(0)
        for invalid in ({'facts': 7}, {'facts': 'ok', 'evidence': 'x' * 513}):
            self.publish(1, **invalid)
            self.assertEqual(len(self.events()), 1)
            self.assertTrue(self.store.inspect_job(self.job_id)['stage_state']['evidence_gap'])
        self.publish(1, facts='fixed')
        self.assertEqual(self.events()[-1]['stage']['facts'], 'fixed')
        self.assertEqual(len(self.events()), 2)

    def test_compact_payload_keeps_stage(self):
        self.publish(0)
        event = self.store.wait_event(self.job_id, poll_interval=0.001)
        event['unrelated_large_field'] = 'x' * 20000
        self.assertEqual(self.store._bounded(event)['stage']['seq'], 0)

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'POSIX FIFO required')
    def test_fifo_records_gap_without_waiting_for_writer(self):
        os.mkfifo(self.root / 'stage.json')
        self.observer.tick()
        self.assertIn('regular file', self.store.inspect_job(self.job_id)['stage_state']['evidence_gap'])

    def test_large_stage_stays_visible_in_local_and_remote_listing(self):
        from remote import RoutedJobStore
        from unittest.mock import patch
        self.publish(3, '阶' * 160, facts='实' * 512, evidence='证' * 512)
        self.assertEqual(self.store.list_jobs()['jobs'][0]['stage_state']['snapshot']['seq'], 3)
        event = self.store.wait_event(self.job_id)
        self.store.ack_event(self.job_id, event['event_id'])
        routed = RoutedJobStore(self.root / 'controller')
        atomic_write_json(routed.state_root / 'remote_jobs' / (self.job_id + '.json'), {})
        with patch.object(routed, 'inspect_job', return_value=self.store.inspect_job(self.job_id)):
            row = routed.list_jobs()['jobs'][0]
        self.assertIsNone(row['pending_event'])
        self.assertEqual(row['stage_state']['snapshot']['stage'], '阶' * 160)

    def test_remote_lock_uses_same_stage_contract(self):
        row = read_json(self.directory / 'job.json')
        row['event_lock'] = 'mkdir'
        atomic_write_json(self.directory / 'job.json', row)
        self.publish(0)
        self.observer.tick()
        self.assertEqual(len(self.events()), 1)


class StageWorkerTest(unittest.TestCase):
    def test_real_worker_captures_short_final_stage_and_bad_file_preserves_exit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            store = JobStore(root / 'state')
            for valid in (True, False):
                code = "import os,json; from pathlib import Path; p=Path(os.environ['SUPERVISOR_STAGE_PATH']); p.write_text(" + (
                    "json.dumps(dict(job_id=os.environ['SUPERVISOR_JOB_ID'],seq=0,stage='scoring')))" if valid else "'{broken')"
                ) + "; raise SystemExit(7)"
                job = store.start_job(name='real-stage', cwd=root, stage_path=root / ('valid.json' if valid else 'bad.json'), command=[sys.executable, '-c', code])
                event = store.wait_event(job['job_id'], poll_interval=0.01)
                if valid:
                    self.assertEqual(event['event_type'], 'stage_changed')
                    store.ack_event(job['job_id'], event['event_id'])
                    event = store.wait_event(job['job_id'], poll_interval=0.01)
                self.assertEqual(event['event_type'], 'failed')
                self.assertEqual(event['exit_code'], 7)


if __name__ == '__main__':
    unittest.main()
