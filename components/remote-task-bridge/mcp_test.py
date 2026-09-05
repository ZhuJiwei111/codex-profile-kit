import importlib.util
import json
import struct
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('remote_mcp', Path(__file__).with_name('mcp.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Socket:
    def __init__(self):
        self.sent = b''
        value = json.dumps({'result': {'success': True, 'contentItems': [{'type': 'inputText', 'text': '{"clientThreadId":"queued"}'}]}}).encode()
        self.buffer = struct.pack('<I', len(value)) + value
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def settimeout(self, timeout): pass
    def connect(self, path): self.path = path
    def sendall(self, value): self.sent += value
    def recv(self, size):
        value, self.buffer = self.buffer[:min(size, 3)], self.buffer[min(size, 3):]
        return value

class Tests(unittest.TestCase):
    def setUp(self):
        # The production helper runs on Linux; Windows tests replace the socket completely.
        self.unix = patch.object(m.socket, 'AF_UNIX', 1, create=True)
        self.unix.start()
        self.addCleanup(self.unix.stop)

    def test_metadata_framing_and_partial_reads(self):
        sock = Socket()
        params = {'name': 'create_thread', 'arguments': {'prompt': '中文'}, '_meta': {
            'x-codex-turn-metadata': json.dumps({'thread_id': 'parent', 'turn_id': 'turn'}), 'openai/tool_call_id': 'call'}}
        with patch.object(m.socket, 'socket', return_value=sock), patch.dict(m.os.environ, {'REMOTE_TASKS_SOCKET': '/test/socket'}):
            response = m.call(params, 3)
        self.assertFalse(response['isError'])
        value = json.loads(sock.sent[4:])
        self.assertEqual(value['params']['callId'], 'call')
        self.assertEqual(value['params']['arguments'], {'prompt': '中文'})
        self.assertEqual(struct.unpack('<I', sock.sent[:4])[0], len(sock.sent[4:]))

    def test_missing_stable_metadata_does_not_connect(self):
        with patch.object(m.socket, 'socket') as create:
            with self.assertRaisesRegex(ValueError, 'Stable executor'):
                m.call({'name': 'create_thread', 'arguments': {'prompt': 'test'}}, 1)
            create.assert_not_called()

    def test_connection_loss_does_not_retry(self):
        sock = Socket()
        sock.buffer = b''
        with patch.object(m.socket, 'socket', return_value=sock) as create, patch.dict(m.os.environ, {'REMOTE_TASKS_SOCKET': '/test/socket'}):
            with self.assertRaisesRegex(RuntimeError, 'outcome may be unknown'):
                m.call({'name': 'create_thread', 'arguments': {'prompt': 'test'}, '_meta': {'threadId': 'p', 'turnId': 't', 'callId': 'c'}}, 1)
            self.assertEqual(create.call_count, 1)

if __name__ == '__main__': unittest.main()
