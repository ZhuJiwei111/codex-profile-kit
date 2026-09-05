import json
import tempfile
import unittest
from pathlib import Path
from configuration import load_config

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.state = self.root/'state'; self.state.mkdir()
        (self.state/'bridge-owner.json').write_text(json.dumps({'component':'remote-task-bridge','stateRoot':str(self.state)}))
        self.file = self.root/'config.json'
        self.config = dict(version=1,enabled=True,stateRoot=str(self.state),sourceApp=str(self.root/'source'),sshExecutable=str(self.root/'ssh.exe'),sshAlias='fixture',hostId='remote-ssh-discovered:fixture',remoteDirectory='/private/bridge',remotePython='/usr/bin/python3',projects=['/project'])
    def load(self):
        self.file.write_text(json.dumps(self.config));return load_config(self.file)
    def test_valid_opt_in(self): self.assertEqual(self.load()['projects'],['/project'])
    def test_disabled(self):
        self.config['enabled']=False
        with self.assertRaisesRegex(ValueError,'disabled'):self.load()
    def test_shell_path_rejected(self):
        self.config['remoteDirectory']='/tmp/a;uname'
        with self.assertRaisesRegex(ValueError,'remote path'):self.load()
    def test_source_overlap_rejected(self):
        self.config['sourceApp']=str(self.state/'source')
        with self.assertRaisesRegex(ValueError,'separate'):self.load()
    def test_wrong_owner_rejected(self):
        (self.state/'bridge-owner.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'ownership'):self.load()
    def test_wrong_host_rejected(self):
        self.config['hostId']='local'
        with self.assertRaisesRegex(ValueError,'SSH binding'):self.load()

if __name__=='__main__':unittest.main()
