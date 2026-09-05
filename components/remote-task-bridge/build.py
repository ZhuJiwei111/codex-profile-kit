"""Version-specific experiment patch. Only changes the task-owned runtime copy."""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import argparse
from configuration import load_config

source = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description='Build a version-specific isolated Desktop adapter; no deployment or network.')
parser.add_argument('--config', required=True)
args = parser.parse_args()
settings = load_config(args.config)
root = Path(settings['stateRoot']).resolve()
staging = root / 'daily-build'
target = staging / 'app.asar'
original = Path(settings['sourceApp']) / 'resources' / 'app.asar'
assert target.resolve().is_relative_to(root.resolve())
staging.mkdir(exist_ok=True)
data = original.read_bytes()
header = json.loads(data[16:16+struct.unpack_from('<I', data, 12)[0]])
base = 8 + struct.unpack_from('<I', data, 4)[0]
entries = []
def walk(tree, prefix=''):
    for name, entry in tree.items():
        path = prefix + name
        if 'files' in entry:
            walk(entry['files'], path + '/')
        elif 'offset' in entry:
            entries.append((path,entry))
walk(header['files'])
config = {
    'command':settings['remotePython'],
    'args':['-u',settings['remoteDirectory']+'/mcp.py'],
    'env':{'REMOTE_TASKS_SOCKET':settings['remoteDirectory']+'/bridge.sock'},
    'enabled':True,
    'enabled_tools':['create_thread'],
    'default_tools_approval_mode':'prompt',
    'tools':{'create_thread':{'approval_mode':'prompt'}},
    'startup_timeout_sec':10,
    'tool_timeout_sec':90,
}
host = json.dumps(settings['hostId'])
paths = json.dumps(settings['projects'])
# Use the exact project assignment getter used by Desktop's list_threads.
condition = ('n.hostId==='+host+'&&(()=>{let scope=l1t();let assignment=e.threadId==null?null:scope.get(fW,$P(Zg(e.threadId)));'
             'let projects=lW(scope).filter(p=>p.hostId===n.hostId&&'+paths+'.includes(p.path));'
             'return assignment?.projectId!=null?projects.some(p=>p.projectId===assignment.projectId):projects.some(p=>p.path===e.cwd)})()')
patches = {
 '.vite/build/main-B6oTeDcE.js': (
    'Ne!=null&&(process.env[pf]=Ne.pipePath);let Pe=',
    'Ne!=null&&(process.env[pf]=Ne.pipePath);await require(p.default.join(process.resourcesPath,"remote-tasks","desktop.cjs")).start({mie,getContext:()=>Fe.getWindowContext()}).catch(()=>null);let Pe='
 ),
 'webview/assets/app-initial-d2e74794629d.js': (
    'if(t.readDeveloperInstructions!=null){let r=await t.readDeveloperInstructions({baseInstructions:a.developerInstructions',
    'if('+condition+'){a.config={...a.config,"mcp_servers.remote_tasks":'+json.dumps(config,separators=(',',':'))+'}}if(t.readDeveloperInstructions!=null){let r=await t.readDeveloperInstructions({baseInstructions:a.developerInstructions'
 )
}
chunks=[]
offset=0
changed=[]
for path,entry in sorted(entries,key=lambda pair:int(pair[1]['offset'])):
    start=base+int(entry['offset'])
    blob=data[start:start+entry['size']]
    if path in patches:
        before,after=patches[path]
        text=blob.decode()
        assert text.count(before)==1,(path,text.count(before))
        blob=text.replace(before,after).encode()
        if path.startswith('webview/'):
            old = 'thread:{id:d.id,kind:`codex`,hostId:l,title:d.name'
            new = 'thread:{id:d.id,kind:`codex`,projectId:e.get(fW,$P(Zg(d.id)))?.projectId??null,hostId:l,title:d.name'
            text = blob.decode()
            assert text.count(old) == 1
            blob = text.replace(old,new).encode()
        # ASAR's existing integrity format requires these fields; not an extra validation digest.
        if 'integrity' in entry:
            integrity=entry['integrity']
            assert integrity['algorithm']=='SHA256'
            block_size=integrity['blockSize']
            integrity['hash']=hashlib.sha256(blob).hexdigest()
            integrity['blocks']=[hashlib.sha256(blob[i:i+block_size]).hexdigest() for i in range(0,len(blob),block_size)]
        changed.append(path)
    entry['offset']=str(offset)
    entry['size']=len(blob)
    offset+=len(blob)
    chunks.append(blob)
assert set(changed)==set(patches)
encoded=json.dumps(header,separators=(',',':'),ensure_ascii=False).encode()
padding=(-len(encoded))%4
size=8+len(encoded)+padding
packed=struct.pack('<IIII',4,size,size-4,len(encoded))+encoded+b'\0'*padding+b''.join(chunks)
# The existing native ASAR integrity resource must describe this experimental archive.
# Keep verification enabled; update only the task-owned executable's fixed-size reference.
native_source = original.parent.parent / 'ChatGPT.exe'
native_target = staging / 'ChatGPT.exe'
native = native_source.read_bytes()
old_reference = hashlib.sha256(data[16:16+struct.unpack_from('<I',data,12)[0]]).hexdigest().encode()
new_reference = hashlib.sha256(encoded).hexdigest().encode()
assert native.count(old_reference) == 1
target.write_bytes(packed)
native_target.write_bytes(native.replace(old_reference,new_reference))
for name in ['core.cjs','desktop.cjs']:
    (staging/'remote-tasks').mkdir(exist_ok=True)
    shutil.copyfile(source/name,staging/'remote-tasks'/name)
(staging/'remote-tasks'/'config.json').write_text(json.dumps(settings,indent=2),encoding='utf8')
print('Patched task-owned archive entries:', *changed, sep='\n')
print('Staged only. Running runtime and original installation untouched.')
