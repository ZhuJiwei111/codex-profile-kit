---
name: personal-defer-and-resume
description: Use when an authorized build, training job, CI wait, migration, artifact generation, or blocking remote watcher is expected to exceed about ten minutes and the same Codex task must resume on command exit or sustained attention evidence; not when work must survive closing the task or restarting the host.
---

# Personal Defer And Resume

Use the bundled runner and `Stop` hook as one same-task waiting primitive. The
runner knows only whether one registered command exited. The command must
represent a terminal completion or attention boundary.

## Choose The Command

- Defer only a non-interactive command already authorized in the current task.
- For remote work, prefer one blocking command such as an SSH scheduler wait or
  project-owned watcher. Treat SSH loss as command failure, not remote-job
  failure.
- Put GPU, log, or artifact conditions in a task-specific watcher with exact
  job identity and a sustained window.
- Aggregate parallel jobs behind one launcher or watcher instead of registering
  several waits. Leave evidence-dependent later phases outside it.
- Treat watcher exit as evidence only; it grants no authority to control the
  underlying job.

Do not use Scheduled tasks, Luna polling tasks, setup tasks, live fallbacks,
relay tasks, or a separate App task. Keep the task and local host running.

## Start And Defer

Register the command with the installed script:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/personal-defer-and-resume/scripts/defer.py" start \
  --name "descriptive command or watcher" \
  --cwd "$PWD" \
  -- command arg1 arg2
```

Authorized `--timeout SECONDS` terminates the process group and records `124`.

After registration, finish the turn. The local Hook waits without model calls.
On `Deferred wait re-arm`, call no tools and end the turn immediately.

Handle user messages normally. New authorization or resource preferences leave
the registered command unchanged and apply only after checking its result. Use
bounded `status` and authoritative job evidence for status requests.

## Resume On Completion Or Attention

First run the prompt's exact `resume --task-dir ...` command. It returns bounded
metadata and atomically acknowledges delivery without returning command output.

- Exit `0` proves only command success; verify intended artifacts or workflow
  state before claiming wider success.
- Exit `124` is an authorized timeout; `125` means the worker vanished without
  a result. Check authoritative state before inferring remote-job status.
- Any other nonzero exit needs diagnosis of the registered command. Read only
  the necessary tail of the private `output.log`.

Continue after recording evidence. Launch phases only when authorized and
ready. Clean acknowledged state when no longer needed:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/personal-defer-and-resume/scripts/defer.py" clean --task-dir <path>
```

## Recovery And Boundaries

Use `list` for this task's registrations, `status` for one, and legacy `inspect`
or `ack` only for recovery. `start` refuses a running or
completed-unacknowledged registration. Completion is delivered at most three
times; afterward the Hook releases normal turns while `list` and the next
`start` still expose it.

The runner cannot cancel and accepts no input or TTY. Clean only acknowledged
state. Keep secrets out of OS-visible arguments.

Read `references/source-notes.md` only when updating provenance or importing
upstream changes.
