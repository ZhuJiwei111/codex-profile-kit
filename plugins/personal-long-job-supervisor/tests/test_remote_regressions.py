"""Regressions from the independent review of SSH access."""
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from durable import atomic_write_json, read_json, locked_events, append_event
from supervisor import JobStore, SupervisorError, WorkerNotStarted
from remote import RemoteClient, RoutedJobStore
from test_supervisor import FakeRuntime
from monitoring import MonitorEngine
import worker
from process_identity import ProcessIdentityError

class ReviewRegressions(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
    def tearDown(self):
        self.temp.cleanup()

    def test_lost_worker_after_sampling_error_keeps_live_target_records(self):
        runtime = FakeRuntime()
        store = JobStore(self.root / 'state', runtime=runtime)
        job = store.start_job(name='orphan', cwd=self.root, command=['fixture'])
        job_id = job['job_id']
        folder = store.job_dir(job_id)
        reg = read_json(folder / 'job.json')
        reg['created_at'] = '2000-01-01T00:00:00Z'
        atomic_write_json(folder / 'job.json', reg)
        atomic_write_json(folder / 'target_process.json', {'pid': 9999, 'start_ticks': 1})
        with locked_events(folder) as data:
            append_event(data, reg, 'supervisor_error', detail='sampling failed')
        store.ack_event(job_id, store.wait_event(job_id)['event_id'])
        runtime.states[job['process']['pid']]['active'] = False
        runtime.states[9999] = {'active': True, 'state': 'running'}
        event = store.wait_event(job_id)
        self.assertEqual(event['reason'], 'worker_lost')
        store.ack_event(job_id, event['event_id'])
        with self.assertRaisesRegex(SupervisorError, 'running target'):
            store.clean_job(job_id)
        self.assertTrue((folder / 'events.json').exists())

    def test_failed_launch_distinguishes_rejected_from_unconfirmed(self):
        for reason, failure in [('worker_not_started', WorkerNotStarted('cannot spawn')),
                                ('launch_unconfirmed', SupervisorError('identity timed out'))]:
            with self.subTest(reason=reason):
                store = JobStore(self.root / reason, runtime=FakeRuntime())
                job_id = 'failed-start'
                with mock.patch.object(store.runtime, 'start', side_effect=failure), self.assertRaises(SupervisorError):
                    store.start_job(name='fixture', request_id=job_id, cwd=self.root, command=['fixture'])
                event = store.wait_event(job_id)
                self.assertEqual(event['reason'], reason)
                self.assertEqual(store.list_jobs()['jobs'][0]['job_id'], job_id)
                store.ack_event(job_id, event['event_id'])
                self.assertFalse(store.inspect_job(job_id)['waitable'])
                if reason == 'worker_not_started':
                    self.assertTrue(store.clean_job(job_id)['cleaned'])
                else:
                    with self.assertRaisesRegex(SupervisorError, 'confirmed terminal'):
                        store.clean_job(job_id)

    def test_two_projects_cannot_claim_same_controller_id(self):
        from concurrent.futures import ThreadPoolExecutor
        clients = []
        for name in ('one', 'two'):
            project = self.root / name
            atomic_write_json(project / '.local/connections.json', {})
            clients.append(RemoteClient(project))
        barrier = threading.Barrier(2)
        def claim(client):
            barrier.wait(timeout=5)
            try:
                client.reserve('same-request', 'test', '/state')
                return client
            except SupervisorError:
                return None
        with mock.patch.dict(os.environ, {'PLJS_STATE_ROOT': str(self.root / 'controller')}):
            with ThreadPoolExecutor(2) as pool:
                winners = [c for c in pool.map(claim, clients) if c]
            self.assertEqual(len(winners), 1)
            winners[0].reserve('same-request', 'test', '/state')
            loser = next(c for c in clients if c is not winners[0])
            self.assertFalse(loser.locator_path('same-request').exists())
            owner = read_json(self.root / 'controller/remote_jobs/same-request.json')
            self.assertEqual(owner['project'], str(winners[0].project))

    def test_explicit_released_host_cleanup_preserves_artifacts_and_replay_guard(self):
        runtime = FakeRuntime()
        store = JobStore(self.root / 'state', runtime=runtime)
        artifact = self.root / 'checkpoint'; artifact.write_text('evidence')
        args = dict(name='released', cwd=str(self.root), command=['/bin/true'],
                    request_id='released-job-0001', event_lock='mkdir', artifacts=[artifact])
        job = store.start_job(**args)
        directory = store.job_dir(job['job_id'])
        original = read_json(directory / 'job.json')
        foreign = dict(original, execution_host={'platform':'linux','boot_id':'released-instance'})
        atomic_write_json(directory / 'job.json', foreign)
        with mock.patch.object(runtime, 'inspect', side_effect=AssertionError('foreign PID must not be inspected')):
            with self.assertRaisesRegex(SupervisorError, 'unverified remote'):
                store.clean_job(job['job_id'])
            self.assertFalse((directory / 'result.json').exists())
            self.assertTrue(store.clean_job(job['job_id'], released_host=True)['release_confirmed_by_caller'])
        self.assertFalse(directory.exists())
        self.assertEqual(artifact.read_text(), 'evidence')
        with self.assertRaisesRegex(SupervisorError, 'already cleaned'):
            store.start_job(**args)
        self.assertEqual(len(runtime.started), 1)

    def test_release_confirmation_does_not_clean_current_instance(self):
        runtime = FakeRuntime()
        store = JobStore(self.root / 'state', runtime=runtime)
        job = store.start_job(name='live', cwd=str(self.root), command=['/bin/true'], event_lock='mkdir')
        with self.assertRaisesRegex(SupervisorError, 'running job'):
            store.clean_job(job['job_id'], released_host=True)
        runtime.states[job['process']['pid']]['active'] = False
        with self.assertRaisesRegex(SupervisorError, 'different remote execution instance'):
            store.clean_job(job['job_id'], released_host=True)

    def test_released_cleanup_uses_selected_target_without_rebinding(self):
        project = self.root / 'project'
        atomic_write_json(project / '.local/connections.json', {
            'default_target':'new','targets':{'new':{'ssh_alias':'new'}},
            'supervisor':{'state_root':'/shared/state'}})
        with mock.patch.dict(os.environ, {'PLJS_STATE_ROOT':str(self.root / 'controller')}):
            client = RemoteClient(project)
            client.reserve('released-job-0002', 'removed', '/shared/state')
            def clean(action, **kwargs):
                self.assertEqual(action, 'clean')
                self.assertEqual(kwargs['target'], 'new')
                self.assertTrue(kwargs['released_host'])
                self.assertEqual(client.locator('released-job-0002')['target'], 'removed')
                return {'cleaned':True}
            with mock.patch.object(client, 'rpc', side_effect=clean):
                client.clean_job('released-job-0002', released_host=True)
            self.assertFalse(client.locator_path('released-job-0002').exists())

    def test_worker_keeps_terminal_result_when_fast_target_identity_is_gone(self):
        for code in (0, 7):
            with self.subTest(code=code):
                atomic_write_json(self.root / 'job.json', {'job_id': 'fast-target-0001', 'monitors': []})
                atomic_write_json(self.root / 'events.json', {'events': [], 'next_event_id': 1})
                target = mock.Mock(pid=123)
                target.poll.return_value = code
                target.wait.return_value = code
                with mock.patch.object(worker, 'require_process_identity', side_effect=[
                        {'pid': 456, 'start_ticks': 1}, ProcessIdentityError('process already exited')]), \
                     mock.patch.object(worker.subprocess, 'Popen', return_value=target), \
                     mock.patch.object(worker, 'MonitorEngine') as engine:
                    self.assertEqual(worker.main(['--job-dir', str(self.root), '--', '/bin/true']), code)
                engine.assert_not_called()
                result = read_json(self.root / 'result.json')
                self.assertEqual(result['exit_code'], code)
                self.assertNotIn('monitor_error', result)
                events = read_json(self.root / 'events.json')['events']
                self.assertEqual([event['event_type'] for event in events],
                                 ['completed' if code == 0 else 'failed'])

    def test_identity_write_failure_preserves_target_exit(self):
        atomic_write_json(self.root / 'job.json', {'job_id': 'identity-write', 'monitors': []})
        atomic_write_json(self.root / 'events.json', {'events': [], 'next_event_id': 1})
        def write(path, value):
            if path.name == 'target_process.json':
                raise OSError('temporary write failure')
            atomic_write_json(path, value)
        target = mock.Mock(pid=123)
        target.wait.return_value = 7
        with mock.patch.object(worker, 'atomic_write_json', side_effect=write), \
             mock.patch.object(worker, 'require_process_identity', return_value={'pid': 123}), \
             mock.patch.object(worker.subprocess, 'Popen', return_value=target):
            self.assertEqual(worker.main(['--job-dir', str(self.root), '--', 'fixture']), 7)
        target.wait.assert_called_once()
        self.assertEqual(read_json(self.root / 'result.json')['exit_code'], 7)
        self.assertEqual([e['event_type'] for e in read_json(self.root / 'events.json')['events']],
                         ['supervisor_error', 'failed'])

    def test_worker_waits_for_live_target_when_identity_cannot_be_read(self):
        atomic_write_json(self.root / 'job.json', {'job_id': 'identity-gap-0001', 'monitors': []})
        atomic_write_json(self.root / 'events.json', {'events': [], 'next_event_id': 1})
        target = mock.Mock(pid=123)
        target.poll.return_value = None
        target.wait.side_effect = [worker.subprocess.TimeoutExpired('fixture', 1), 0]
        with mock.patch.object(worker, 'require_process_identity', side_effect=[
                {'pid': 456, 'start_ticks': 1}, ProcessIdentityError('identity unavailable')]), \
             mock.patch.object(worker.subprocess, 'Popen', return_value=target), \
             mock.patch.object(worker, 'MonitorEngine') as engine:
            self.assertEqual(worker.main(['--job-dir', str(self.root), '--', '/bin/true']), 0)
        engine.assert_not_called()
        self.assertEqual(target.wait.call_count, 2)
        self.assertEqual(read_json(self.root / 'result.json')['exit_code'], 0)
        self.assertEqual([event['event_type'] for event in read_json(self.root / 'events.json')['events']],
                         ['supervisor_error', 'completed'])

    def test_clean_racing_delayed_replay_never_launches_twice(self):
        runtime = FakeRuntime()
        store = JobStore(self.root / 'state', runtime=runtime)
        args = dict(name='race', cwd=str(self.root), command=['/bin/true'],
                    request_id='race-job-0001', event_lock='mkdir')
        job = store.start_job(**args)
        directory = store.job_dir(job['job_id'])
        atomic_write_json(directory / 'result.json', {'exit_code': 0, 'finished_at': '2026-11-19T00:00:00Z'})
        runtime.states[job['process']['pid']]['active'] = False
        event = store.inspect_job(job['job_id'])['pending_event']
        store.ack_event(job['job_id'], event['event_id'])
        entered, resume = threading.Event(), threading.Event()
        original = Path.mkdir
        errors = []
        def mkdir(path, *a, **kw):
            if path == directory and threading.current_thread().name == 'replay':
                entered.set()
                if not resume.wait(5): raise AssertionError('replay timeout')
            return original(path, *a, **kw)
        def replay():
            try: store.start_job(**args)
            except SupervisorError as error: errors.append(str(error))
        with mock.patch.object(Path, 'mkdir', mkdir):
            thread = threading.Thread(target=replay, name='replay')
            thread.start()
            try:
                self.assertTrue(entered.wait(2))
                store.clean_job(job['job_id'])
            finally:
                resume.set()
                thread.join(5)
        self.assertEqual(len(runtime.started), 1)
        self.assertFalse(directory.exists())
        self.assertTrue(any('already cleaned' in error for error in errors))

    def test_local_hostname_change_keeps_process_observation(self):
        store = JobStore(self.root / 'state', runtime=FakeRuntime())
        with mock.patch('supervisor.execution_host_identity', return_value={'host': 'a'}):
            job = store.start_job(name='local', cwd=str(self.root), command=['/bin/true'])
        with mock.patch('supervisor.execution_host_identity', return_value={'host': 'b'}):
            row = store.inspect_job(job['job_id'])
        self.assertEqual(row['status'], 'running')
        self.assertTrue(row['waitable'])
        self.assertIsNone(row['pending_event'])

    def test_linux_flock_still_rejects_foreign_execution_identity(self):
        store = JobStore(self.root / 'state', runtime=FakeRuntime())
        with mock.patch('supervisor.execution_host_identity', return_value={'platform': 'linux', 'boot_id': 'a'}):
            job = store.start_job(name='linux', cwd=str(self.root), command=['/bin/true'])
        with mock.patch('supervisor.execution_host_identity', return_value={'platform': 'linux', 'boot_id': 'b'}), \
             mock.patch.object(store.runtime, 'inspect', side_effect=AssertionError('foreign PID inspected')):
            view = store.inspect_job(job['job_id'])
        self.assertEqual(view['status'], 'execution_host_unverified')
        self.assertIsNone(view['pending_event'])

    def test_native_wait_skips_unverified_and_delivers_healthy_event(self):
        store = JobStore(self.root / 'state', runtime=FakeRuntime())
        first = store.start_job(name='foreign', cwd=str(self.root), command=['/bin/true'], event_lock='mkdir')
        second = store.start_job(name='healthy', cwd=str(self.root), command=['/bin/true'])
        p = store.job_dir(first['job_id']) / 'job.json'
        row = read_json(p);row['execution_host'] = {'platform': 'linux', 'boot_id': 'foreign'};atomic_write_json(p, row)
        atomic_write_json(store.job_dir(second['job_id']) / 'result.json', {'exit_code': 0, 'finished_at': '2026-11-19T00:00:00Z'})
        self.assertEqual(store.wait_any([first['job_id'], second['job_id']])['job_id'], second['job_id'])

    def test_remote_groups_skip_unverified_without_cancelling_healthy(self):
        with mock.patch.dict(os.environ, {'PLJS_STATE_ROOT': str(self.root / 'controller')}):
            client = self.client()
            client.reserve('foreign-group-01', 'a', '/shared/state')
            client.reserve('healthy-group-02', 'b', '/shared/state')
            def waiting(self, ids, **kwargs):
                if ids == ['foreign-group-01']:
                    raise SupervisorError('SSH request failed: no waitable execution target; execution host unverified')
                return {'job_id': ids[0], 'event_id': 1}
            with mock.patch.object(RemoteClient, 'wait_any', waiting):
                event = RoutedJobStore().wait_any(['foreign-group-01', 'healthy-group-02'])
            self.assertEqual(event['job_id'], 'healthy-group-02')

    def test_worker_keeps_result_when_event_lock_is_unavailable(self):
        atomic_write_json(self.root / 'job.json', {'monitors': []})
        target = mock.Mock(pid=123)
        target.wait.return_value = 0
        with mock.patch.object(worker, 'require_process_identity', return_value={'pid': 123, 'start_ticks': 1}), \
             mock.patch.object(worker.subprocess, 'Popen', return_value=target), \
             mock.patch.object(worker.MonitorEngine, 'tick', side_effect=RuntimeError('event lock busy')), \
             mock.patch.object(worker, 'locked_events', side_effect=RuntimeError('event lock busy')):
            self.assertEqual(worker.main(['--job-dir', str(self.root), '--', '/bin/true']), 0)
        target.wait.assert_called_once()
        self.assertEqual(read_json(self.root / 'result.json')['exit_code'], 0)
        self.assertIn('event lock busy', read_json(self.root / 'result.json')['monitor_error'])

    def test_last_tick_error_flushes_when_terminal_lock_recovers(self):
        registration = {'job_id': 'last-tick-job-01', 'monitors': [], 'event_lock': 'mkdir'}
        atomic_write_json(self.root / 'job.json', registration)
        atomic_write_json(self.root / 'events.json', {'events': [], 'next_event_id': 1})
        target = mock.Mock(pid=123)
        target.wait.return_value = 0
        attempts = []
        def acquire(path):
            attempts.append(1)
            if len(attempts) == 1: raise RuntimeError('event lock busy')
            return locked_events(path)
        with mock.patch.object(worker, 'require_process_identity', return_value={'pid': 123, 'start_ticks': 1}), \
             mock.patch.object(worker.subprocess, 'Popen', return_value=target), \
             mock.patch.object(worker.MonitorEngine, 'tick', side_effect=RuntimeError('monitor failed')), \
             mock.patch.object(worker, 'locked_events', side_effect=acquire):
            self.assertEqual(worker.main(['--job-dir', str(self.root), '--', '/bin/true']), 0)
        self.assertEqual([e['event_type'] for e in read_json(self.root / 'events.json')['events']],
                         ['supervisor_error', 'completed'])

    def test_reconcile_retains_error_when_terminal_event_lock_was_unavailable(self):
        store = JobStore(self.root / 'state', runtime=FakeRuntime())
        job = store.start_job(name='deferred-error', cwd=str(self.root), command=['/bin/true'])
        atomic_write_json(store.job_dir(job['job_id']) / 'result.json',
                          {'exit_code': 0, 'finished_at': '2026-11-19T00:00:00Z', 'monitor_error': 'monitor failed'})
        for _ in range(2): store.inspect_job(job['job_id'])
        self.assertEqual([e['event_type'] for e in read_json(store.job_dir(job['job_id']) / 'events.json')['events']],
                         ['supervisor_error', 'completed'])

    def test_persistent_monitor_corruption_still_publishes_error(self):
        registration = {'job_id': 'corrupt-job-0001', 'created_epoch': 0,
                        'event_lock': 'mkdir', 'monitors': [
                            {'monitor_id': 'hb', 'kind': 'heartbeat_stale', 'sample_interval_seconds': 1}]}
        atomic_write_json(self.root / 'job.json', registration)
        atomic_write_json(self.root / 'events.json', {'events': [], 'next_event_id': 1,
                         'monitor_states': {'hb': {'last_dispatch_epoch': 'invalid'}}})
        target = mock.Mock(pid=123)
        target.wait.side_effect = [worker.subprocess.TimeoutExpired('fixture', 1), 0]
        with mock.patch.object(worker, 'require_process_identity', return_value={'pid': 123, 'start_ticks': 1}), \
             mock.patch.object(worker.subprocess, 'Popen', return_value=target):
            self.assertEqual(worker.main(['--job-dir', str(self.root), '--', '/bin/true']), 0)
        self.assertEqual(target.wait.call_count, 2)
        self.assertEqual([e['event_type'] for e in read_json(self.root / 'events.json')['events']],
                         ['supervisor_error', 'completed'])
        self.assertEqual(read_json(self.root / 'result.json')['exit_code'], 0)

    def test_sampling_outside_lock_preserves_concurrent_ack(self):
        registration = {'job_id': 'sample-job-0001', 'created_epoch': 0,
                        'event_lock': 'mkdir', 'monitors': [
                            {'monitor_id': 'hb', 'kind': 'heartbeat_stale', 'sample_interval_seconds': 1}]}
        atomic_write_json(self.root / 'job.json', registration)
        atomic_write_json(self.root / 'events.json', {'events': [], 'next_event_id': 1, 'monitor_states': {}})
        engine = MonitorEngine(self.root, registration, 123)
        def sample(data, monitor, now):
            # A real cooperating writer can take the lock while sampling occurs.
            with locked_events(self.root) as current:
                event = append_event(current, registration, 'attention', reason='concurrent')
                event['acknowledged_at'] = 'already-consumed'
            append_event(data, registration, 'attention', reason='sampled')
        with mock.patch.object(engine, '_sample_heartbeat', side_effect=sample):
            engine.tick(now=100)
        events = read_json(self.root / 'events.json')['events']
        self.assertEqual([e['event_id'] for e in events], [1, 2])
        self.assertEqual(events[0]['acknowledged_at'], 'already-consumed')
        self.assertEqual(events[1]['reason'], 'sampled')

    def client(self, target='a'):
        project = self.root / 'project'
        atomic_write_json(project / '.local/connections.json', {
            'default_target': 'a', 'targets': {'a': {'ssh_alias': 'a'}, 'b': {'ssh_alias': 'b'}},
            'supervisor': {'state_root': '/shared/state'}})
        return RemoteClient(project, target=target)

    def test_invalid_target_does_not_reserve_and_corrected_retry_works(self):
        with mock.patch.dict(os.environ, {'PLJS_STATE_ROOT': str(self.root / 'controller')}):
            bad = self.client('missing')
            args = dict(request_id='invalid-target-0001', name='test', cwd='/shared', command=['/bin/true'])
            with self.assertRaisesRegex(SupervisorError, 'registered target'):
                bad.start_job(**args)
            self.assertFalse(bad.locator_path(args['request_id']).exists())
            self.assertFalse((self.root / 'controller/remote_jobs').exists())
            good = self.client('a')
            with mock.patch.object(good, 'rpc', return_value={'job_id': args['request_id']}):
                self.assertEqual(good.start_job(**args)['job_id'], args['request_id'])

    def test_released_host_missing_index_can_be_read_without_rebinding(self):
        with mock.patch.dict(os.environ, {'PLJS_STATE_ROOT': str(self.root / 'controller')}):
            client = self.client()
            client.via = 'a'
            with mock.patch.object(client, 'rpc', return_value={'status': 'execution_host_unverified'}) as rpc:
                self.assertEqual(client.inspect_job('released-job-0001')['status'], 'execution_host_unverified')
                rpc.assert_called_once_with('inspect', job_id='released-job-0001')
            self.assertFalse(client.locator_path('released-job-0001').exists())
            self.assertFalse((self.root / 'controller/remote_jobs').exists())
            with self.assertRaises(FileNotFoundError):
                client.clean_job('released-job-0001')

    def test_lost_multi_node_index_only_restores_verified_or_terminal_jobs(self):
        with mock.patch.dict(os.environ, {'PLJS_STATE_ROOT': str(self.root / 'controller')}):
            client = self.client()
            rows = {'execution_host': {'node': 'a'}, 'jobs': [
                {'job_id': 'node-a-job-0001', 'execution_host': {'node': 'a'}, 'terminal': False},
                {'job_id': 'node-b-job-0002', 'execution_host': {'node': 'b'}, 'terminal': False},
                {'job_id': 'done-b-job-0003', 'execution_host': {'node': 'b'}, 'terminal': True}]}
            with mock.patch.object(client, 'rpc', return_value=rows): result = client.recover()
            self.assertEqual(result['unresolved'], ['node-b-job-0002'])
            self.assertFalse(client.locator_path('node-b-job-0002').exists())
            self.assertEqual(result['recovered'], ['node-a-job-0001', 'done-b-job-0003'])
            other = self.client('b')
            rows['execution_host'] = {'node': 'b'}
            with mock.patch.object(other, 'rpc', return_value=rows): other.recover()
            self.assertEqual(other.locator('node-a-job-0001')['target'], 'a')
            self.assertEqual(other.locator('node-b-job-0002')['target'], 'b')

if __name__ == '__main__': unittest.main()
