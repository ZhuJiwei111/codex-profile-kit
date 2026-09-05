"""Remote stdio adapter for the isolated Desktop; no shell or creation retries."""
import json
import os
import socket
import struct
import sys
import errno
import stat
from pathlib import Path

def prepare_socket():
    target = Path(__file__).resolve().parent / 'bridge.sock'
    try:
        info = target.lstat()
    except FileNotFoundError:
        return
    if not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.getuid():
        raise RuntimeError('Refusing to remove an unexpected socket path')
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as probe:
        probe.settimeout(2)
        try:
            probe.connect(str(target))
        except OSError as error:
            if error.errno != errno.ECONNREFUSED:
                raise
        else:
            raise RuntimeError('An active bridge already owns this socket')
    # Only remove the exact unchanged task-owned socket after proving no listener.
    current = target.lstat()
    if (current.st_dev, current.st_ino) != (info.st_dev, info.st_ino):
        raise RuntimeError('Socket changed during startup')
    target.unlink()

TOOL = {'name': 'create_thread', 'description': 'Create a task in the current authorized remote project, only when the user explicitly requests a new task. Native approval is required. Git projects default to worktree; select local only when the user requests the saved project directly. Return queued identities honestly. Never automatically retry an unknown creation result.',
        'inputSchema': {'type': 'object', 'properties': {
            'prompt': {'type': 'string', 'minLength': 1},
            'title': {'type': 'string', 'minLength': 1},
            'environment': {'type': 'string', 'enum': ['local', 'worktree']}},
            'required': ['prompt'], 'additionalProperties': False}}

def receive(sock, size):
    data = bytearray()
    while len(data) < size:
        part = sock.recv(size - len(data))
        if not part:
            raise RuntimeError('Connection lost; outcome may be unknown. Do not retry automatically.')
        data.extend(part)
    return bytes(data)

def metadata_id(meta, names, nested):
    for name in names:
        value = meta.get(name)
        if isinstance(value, str) and value:
            return value
    value = meta.get(nested)
    return value.get('id') if isinstance(value, dict) else None

def call(params, request_id):
    if params.get('name') != 'create_thread':
        raise ValueError('Unsupported tool')
    args = params.get('arguments', {})
    if not isinstance(args, dict) or set(args) - {'prompt', 'title', 'environment'}:
        raise ValueError('Unsupported arguments')
    if not isinstance(args.get('prompt'), str) or not args['prompt'].strip():
        raise ValueError('prompt is required')
    meta = params.get('_meta', {})
    turn = meta.get('x-codex-turn-metadata', {})
    if isinstance(turn, str):
        turn = json.loads(turn)
    tid = metadata_id(meta, ['openai/threadId', 'openai/thread_id', 'codexThreadId', 'codex_thread_id', 'threadId', 'thread_id'], 'thread') or turn.get('thread_id')
    turn_id = metadata_id(meta, ['openai/turnId', 'openai/turn_id', 'codexTurnId', 'codex_turn_id', 'turnId', 'turn_id'], 'turn') or turn.get('turn_id')
    call_id = metadata_id(meta, ['openai/toolCallId', 'openai/tool_call_id', 'codexCallId', 'codex_call_id', 'callId', 'call_id'], 'call')
    if not tid or not turn_id or not call_id:
        raise ValueError('Stable executor thread, turn and call metadata required; no creation was dispatched')
    payload = json.dumps({'jsonrpc': '2.0', 'id': request_id, 'method': 'tools/call', 'params': {
        'namespace': 'codex_app', 'tool': 'create_thread', 'arguments': args,
        'threadId': tid, 'turnId': turn_id, 'callId': call_id}}).encode()
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(65)
        sock.connect(os.environ['REMOTE_TASKS_SOCKET'])
        sock.sendall(struct.pack('<I', len(payload)) + payload)
        size = struct.unpack('<I', receive(sock, 4))[0]
        if size > 8 * 1024 * 1024:
            raise RuntimeError('Oversize response; do not automatically retry')
        response = json.loads(receive(sock, size))
    if 'error' in response:
        raise RuntimeError(response['error']['message'])
    result = response['result']
    return {'content': [{'type': 'text', 'text': item['text']} for item in result['contentItems'] if item['type'] == 'inputText'], 'isError': not result['success']}

def main():
    for line in sys.stdin:
        message = json.loads(line)
        if 'id' not in message:
            continue
        try:
            method = message['method']
            if method == 'initialize':
                result = {'protocolVersion': message['params']['protocolVersion'], 'capabilities': {'tools': {}}, 'serverInfo': {'name': 'remote_tasks', 'version': '1.0.0'}}
            elif method == 'tools/list':
                result = {'tools': [TOOL]}
            elif method == 'ping':
                result = {}
            elif method == 'tools/call':
                result = call(message['params'], message['id'])
            else:
                raise ValueError('Unsupported method')
            response = {'jsonrpc': '2.0', 'id': message['id'], 'result': result}
        except Exception as error:
            response = {'jsonrpc': '2.0', 'id': message['id'], 'error': {'code': -32000, 'message': str(error)}}
        print(json.dumps(response), flush=True)

if __name__ == '__main__':
    if sys.argv[1:] == ['--prepare-socket']:
        prepare_socket()
    else:
        main()
