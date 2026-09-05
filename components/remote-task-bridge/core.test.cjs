const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {createHandler} = require('./core.cjs');
const result = x => ({success:true,contentItems:[{type:'inputText',text:JSON.stringify(x)}]});
function fixture(t, options={}) {
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'remote-tasks-test-'));
  t.after(()=>fs.rmSync(root,{recursive:true})); // Exact directory returned by mkdtemp for this test.
  const config={hostId:'remote-test',projects:['/project']};
  const p={namespace:'codex_app',tool:'create_thread',threadId:'parent',turnId:'turn',callId:'call',arguments:{prompt:'only reply OK'}};
  const calls=[];
  const invoke=async(tool,args)=> {
    if(tool==='read_thread')return result({thread:{id:'parent',hostId:'remote-test',cwd:options.cwd??'/project',projectId:options.projectId},turns:[{id:'turn',status:'inProgress'}]});
    if(tool==='list_projects')return result({projects:[{projectId:'project',projectKind:'remote',hostId:'remote-test',path:'/project',isGitRepository:options.git??true}]});
    calls.push(args); return options.create?options.create():result({clientThreadId:'queued',hostId:'remote-test'});
  };
  return {p,calls,handler:createHandler({root,config,invoke}),restart:()=>createHandler({root,config,invoke})};
}
test('Git defaults to worktree and preserves queued result across restart',async t=>{
  const f=fixture(t);const r=await f.handler(f.p);assert.equal(f.calls[0].target.environment.type,'worktree');
  assert.equal(JSON.parse(r.contentItems[0].text).clientThreadId,'queued');
  assert.deepEqual(await f.restart()(f.p),r);assert.equal(f.calls.length,1);
});
test('explicit local, titles and prompts are forwarded',async t=>{
  const f=fixture(t);f.p.arguments={prompt:'中文 task',title:'标题',environment:'local'};await f.handler(f.p);
  assert.equal(f.calls[0].prompt,'中文 task');assert.equal(f.calls[0].title,'标题');assert.equal(f.calls[0].target.environment.type,'local');
});
test('non-Git defaults to local; explicit worktree rejected',async t=>{
  const f=fixture(t,{git:false});await f.handler(f.p);assert.equal(f.calls[0].target.environment.type,'local');
  f.p.callId='second';f.p.arguments.environment='worktree';await assert.rejects(f.handler(f.p),/requires a Git/);assert.equal(f.calls.length,1);
});
test('worktree source uses Desktop assignment; ambiguous source rejected',async t=>{
  const f=fixture(t,{cwd:'/worktrees/abcd/project',projectId:'project'});await f.handler(f.p);assert.equal(f.calls.length,1);
  const g=fixture(t,{cwd:'/worktrees/abcd/project'});await assert.rejects(g.handler(g.p),/ambiguous/);assert.equal(g.calls.length,0);
});
test('foreign project and extra target rejected without dispatch',async t=>{
  const f=fixture(t,{projectId:'foreign'});await assert.rejects(f.handler(f.p),/unauthorized/);
  f.p.arguments.hostId='local';await assert.rejects(f.handler(f.p),/Unsupported/);assert.equal(f.calls.length,0);
});
test('concurrent duplicates dispatch once',async t=>{
  let finish;const f=fixture(t,{create:()=>new Promise(r=>finish=r)});
  const first=f.handler(f.p);await new Promise(r=>setImmediate(r));
  await assert.rejects(f.handler(f.p),/in progress/);finish(result({threadId:'child'}));await first;assert.equal(f.calls.length,1);
});
test('post-dispatch loss remains unknown after restart',async t=>{
  const f=fixture(t,{create:()=>{throw Error('connection lost')}});await assert.rejects(f.handler(f.p),/connection lost/);
  await assert.rejects(f.restart()(f.p),/outcome unknown/);assert.equal(f.calls.length,1);
});
test('missing metadata and cancellation before dispatch do not create',async t=>{
  const f=fixture(t);await assert.rejects(f.handler({...f.p,callId:undefined}),/Invalid callId/);
  const c=new AbortController();c.abort();await assert.rejects(f.handler(f.p,c.signal));assert.equal(f.calls.length,0);
});
