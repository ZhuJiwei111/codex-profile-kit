"""Host-local opt-in configuration; never imported by profile_sync."""
import json
import re
from pathlib import Path

def load_config(file):
    value = json.loads(Path(file).read_text(encoding='utf-8-sig'))
    if value.get('version') != 1 or value.get('enabled') is not True:
        raise ValueError('Bridge is disabled; explicit host-local opt-in required')
    alias = value.get('sshAlias', '')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', alias) or value.get('hostId') != 'remote-ssh-discovered:' + alias:
        raise ValueError('Invalid SSH binding')
    for key in ['remoteDirectory', 'remotePython']:
        path = value.get(key, '')
        if not re.fullmatch(r'/[A-Za-z0-9_./-]+', path) or '..' in path.split('/'):
            raise ValueError('Invalid remote path')
    if not value.get('projects') or not all(isinstance(p, str) and p.startswith('/') and '..' not in p.split('/') for p in value['projects']):
        raise ValueError('Explicit absolute project paths required')
    for key in ['stateRoot', 'sourceApp', 'sshExecutable']:
        if not Path(value.get(key, '')).is_absolute():
            raise ValueError('Absolute local paths required')
    state, source = Path(value['stateRoot']).resolve(), Path(value['sourceApp']).resolve()
    if state == source or state in source.parents or source in state.parents:
        raise ValueError('Source and state must be separate')
    owner = json.loads((state/'bridge-owner.json').read_text(encoding='utf-8-sig'))
    if owner.get('component') != 'remote-task-bridge' or Path(owner.get('stateRoot', '')).resolve() != state:
        raise ValueError('State ownership mismatch')
    return value
