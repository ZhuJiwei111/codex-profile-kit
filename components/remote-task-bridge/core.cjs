'use strict';
const fs = require('node:fs');
const path = require('node:path');

function argumentsFor(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value) ||
      Object.keys(value).some(k => !['prompt', 'title', 'environment'].includes(k)))
    throw Error('Unsupported arguments');
  if (typeof value.prompt !== 'string' || !value.prompt.trim()) throw Error('prompt is required');
  if (value.title !== undefined && (typeof value.title !== 'string' || !value.title.trim())) throw Error('Invalid title');
  if (value.environment !== undefined && !['local', 'worktree'].includes(value.environment)) throw Error('Invalid environment');
  return {...value};
}
function resolveProject(thread, projects, config) {
  if (thread.hostId !== config.hostId) throw Error('Source host is not authorized');
  const candidates = projects.filter(p => p.projectKind === 'remote' && p.hostId === config.hostId);
  const matches = thread.projectId != null
    ? candidates.filter(p => p.projectId === thread.projectId)
    : candidates.filter(p => p.path === thread.cwd);
  if (matches.length !== 1 || !config.projects.includes(matches[0].path))
    throw Error('Source project is ambiguous or unauthorized');
  return matches[0];
}
function createHandler({root, config, invoke, log = () => {}}) {
  const directory = path.join(root, 'requests');
  fs.mkdirSync(directory, {recursive: true});
  const active = new Set();
  return async (p, signal) => {
    if (p.namespace !== 'codex_app' || p.tool !== 'create_thread') throw Error('Unsupported tool');
    const args = argumentsFor(p.arguments);
    for (const key of ['threadId', 'turnId', 'callId']) {
      if (typeof p[key] !== 'string' || !/^[a-zA-Z0-9_-]{1,160}$/.test(p[key])) throw Error(`Invalid ${key}`);
    }
    // Nested identifiers avoid path traversal and filename-length problems; no content digests.
    const parentDir = path.join(directory, p.threadId, p.turnId);
    fs.mkdirSync(parentDir, {recursive: true});
    const file = path.join(parentDir, p.callId + '.json');
    const old = fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')) : null;
    if (old) {
      if (old.state === 'completed') return old.result;
      throw Error(active.has(file) ? 'Request is in progress; do not create again' : 'Creation outcome unknown; inspect existing tasks before a new call');
    }
    const decode = result => {
      if (!result?.success) throw Error('Desktop verification failed');
      return JSON.parse(result.contentItems.find(i => i.type === 'inputText').text);
    };
    const parent = decode(await invoke('read_thread', {hostId: config.hostId, threadId: p.threadId, turnLimit: 1}, p, signal, '-verify'));
    if (parent.thread?.id !== p.threadId || parent.turns?.[0]?.id !== p.turnId || parent.turns[0].status !== 'inProgress')
      throw Error('Source is not the current running turn');
    const projects = decode(await invoke('list_projects', {}, p, signal, '-projects')).projects;
    const project = resolveProject(parent.thread, projects, config);
    if (typeof project.isGitRepository !== 'boolean') throw Error('Project Git status unavailable');
    const environment = args.environment ?? (project.isGitRepository ? 'worktree' : 'local');
    if (environment === 'worktree' && !project.isGitRepository) throw Error('Worktree requires a Git project');
    signal?.throwIfAborted();
    // An exclusive durable record is the final gate immediately before dispatch.
    try { fs.writeFileSync(file, JSON.stringify({state: 'dispatched', projectId: project.projectId}), {flag: 'wx'}); }
    catch (error) { if (error.code === 'EEXIST') throw Error('Request already recorded; do not create again'); throw error; }
    active.add(file);
    log('create-dispatched', {threadId: p.threadId, turnId: p.turnId, callId: p.callId, projectId: project.projectId, environment});
    try {
      const result = await invoke('create_thread', {
        prompt: args.prompt, ...(args.title === undefined ? {} : {title: args.title}),
        target: {type: 'project', projectId: project.projectId, environment: {type: environment}}
      }, p, signal, '');
      const temp = file + '.tmp';
      fs.writeFileSync(temp, JSON.stringify({state: 'completed', result}), {flag: 'wx'});
      fs.renameSync(temp, file);
      log('create-returned', {threadId: p.threadId, callId: p.callId, success: result?.success === true});
      return result;
    } finally { active.delete(file); }
  };
}
module.exports = {createHandler, argumentsFor, resolveProject};
