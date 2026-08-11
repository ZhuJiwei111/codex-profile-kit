---
name: personal-defer-and-resume
description: Defer an authorized non-interactive local or blocking remote command, wait without model polling, and resume the same Codex task when the command exits or a task-specific watchdog reports sustained attention evidence. Use for builds, training jobs, CI watchers, migrations, artifact generation, and exact job wait commands expected to exceed about ten minutes. Not for work that must survive closing the task or restarting the host.
---

# Personal Defer And Resume

Use the bundled runner and `Stop` hook as one same-task waiting primitive. The
runner knows only whether the registered command exited; the command itself
must represent terminal completion or an attention condition.

## Choose The Command

- Run ordinary foreground commands expected to finish within about ten minutes.
- Defer only a non-interactive command already authorized in the current task.
- For remote work, prefer one blocking command such as an SSH scheduler wait or
  a project-owned watcher. A dropped SSH connection is a command failure, not
  proof that the remote job failed.
- Encode GPU, log, or artifact attention conditions in a task-specific watcher.
  Require a sustained window and exact job identity; never alert on one sample.
- A watcher reports evidence only. Monitoring never authorizes cancellation,
  restart, repair, retry, reconfiguration, or cleanup of the underlying job.

Do not use Scheduled tasks, Luna polling tasks, setup tasks, live fallbacks,
relay tasks, or a separate App task for this workflow. Keep Codex Desktop, the
current task, and the local host running. Closing the task or restarting the
host is outside this contract.

## Start And Defer

Resolve the installed script under the active Codex home, then register the
command:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/personal-defer-and-resume/scripts/defer.py" start \
  --name "descriptive command or watcher" \
  --cwd "$PWD" \
  -- command arg1 arg2
```

Use `--timeout SECONDS` only when the user authorized that time limit. A timeout
terminates the registered command process group and records exit code `124`.

After registration succeeds, finish the turn. Do not poll, inspect logs, or
start another monitor. The local Hook checks state without model calls. About
every 50 minutes it may wake the current model once to re-arm the Hook; on a
`Deferred wait re-arm` prompt, call no tools and end the turn immediately.

## Resume On Completion Or Attention

On a completion prompt:

1. Inspect bounded result metadata:

   ```bash
   python3 "${CODEX_HOME:-$HOME/.codex}/skills/personal-defer-and-resume/scripts/defer.py" inspect --task-dir <path>
   ```

2. Read only the necessary tail of the recorded output when the result needs
   diagnosis. Treat exit as command completion or watcher attention, not proof
   that a wider workflow succeeded.
3. Acknowledge the wake after recording the evidence:

   ```bash
   python3 "${CODEX_HOME:-$HOME/.codex}/skills/personal-defer-and-resume/scripts/defer.py" ack --task-dir <path>
   ```

4. Continue the original task. Remove acknowledged runtime state when it is no
   longer needed:

   ```bash
   python3 "${CODEX_HOME:-$HOME/.codex}/skills/personal-defer-and-resume/scripts/defer.py" clean --task-dir <path>
   ```

## Recovery And Boundaries

Use `list` for registrations owned by the current task and `status` for one
registration. A missing worker records exit code `125`; do not infer what
happened to an underlying remote job without checking its authoritative state.

The runner has no cancel operation. Do not force-clean unacknowledged state.
Commands receive no interactive input or TTY. Do not place secrets in command
arguments; persistent metadata omits them, but the operating system may expose
live process arguments.

Read `references/source-notes.md` only when updating provenance or importing
upstream changes.
