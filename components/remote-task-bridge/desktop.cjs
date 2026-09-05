'use strict';
const fs = require('node:fs');
const path = require('node:path');
const net = require('node:net');
const {spawn} = require('node:child_process');
const {createHandler} = require('./core.cjs');
exports.start = async ({mie, getContext}) => {
  const root = path.join(process.env.REMOTE_TASKS_HOME, 'daily-v1');
  fs.mkdirSync(root, {recursive: true});
  const config = JSON.parse(fs.readFileSync(path.join(__dirname, 'config.json'), 'utf8'));
  const log = (event, detail = {}) => fs.appendFileSync(path.join(root, 'events.jsonl'), JSON.stringify({time: new Date().toISOString(), event, ...detail}) + '\n');
  let relay, bridge, ssh;
  const clients = new Set();
  const stop = () => {
    ssh?.kill();
    for (const client of clients) client.destroy();
    relay?.close();
  };
  process.once('exit', stop);
  try {
    const pipe = `\\\\.\\pipe\\codex-remote-tasks-${process.pid}`;
    const invoke = (tool, args, p, signal, suffix) => getContext().callDynamicAppTool({hostId: config.hostId,
      params: {...p, tool, arguments: args, callId: p.callId + suffix}}, signal);
    const handler = createHandler({root, config, invoke, log});
    bridge = await mie({pipePath: pipe, listTools: async () => [], callTool: (r, s) => handler(r.params, s)});
    relay = net.createServer(socket => {
      clients.add(socket);
      const target = net.createConnection(pipe);
      socket.pipe(target); target.pipe(socket);
      socket.on('error', () => target.destroy()); target.on('error', () => socket.destroy());
      socket.on('close', () => {clients.delete(socket); target.destroy();});
      target.on('close', () => socket.destroy());
    });
    await new Promise((resolve, reject) => {relay.once('error', reject); relay.listen(0, '127.0.0.1', resolve);});
    const remoteSocket = config.remoteDirectory + '/bridge.sock';
    ssh = spawn(config.sshExecutable, ['-N', '-T', '-o', 'BatchMode=yes', '-o', 'ExitOnForwardFailure=yes',
      '-o', 'StreamLocalBindUnlink=yes', '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=2',
      '-R', `${remoteSocket}:127.0.0.1:${relay.address().port}`, config.sshAlias],
      {windowsHide: true, stdio: ['ignore', 'ignore', 'pipe']});
    ssh.stderr.on('data', () => {}); // Do not persist connection diagnostics containing arbitrary data.
    ssh.on('error', () => {log('channel-unavailable'); stop();});
    ssh.on('exit', (code) => {log('channel-stopped', {code}); for (const c of clients) c.destroy(); relay.close();});
    fs.writeFileSync(path.join(root, 'runtime.json'), JSON.stringify({desktopPid: process.pid, sshPid: ssh.pid, remoteSocket}));
    log('bridge-started'); // SSH startup is asynchronous; this does not claim the tunnel is ready.
    return {stop, bridge};
  } catch (error) {
    stop(); log('extension-unavailable', {errorType: error.name});
    return null;
  }
};
