---
name: supervise-long-jobs
description: Launch and supervise an already-authorized non-interactive local command expected to run longer than about ten minutes when the current Codex task should resume after completion, failure, or an explicit stale-heartbeat condition. Use event-driven detached-process waiting instead of Goal polling, repeated exec polling, Scheduled tasks, Stop hooks, or ad hoc background terminals. Also use to inspect, reconnect to, acknowledge, or clean registrations created by this supervisor. Do not use for interactive commands, short commands, unauthorized resource use, experiment orchestration, or automatic cancel/retry/restart/reconfiguration.
---

# Supervise Long Jobs

Keep the process and logs in the host. Return to the model only for a durable event.

## Launch

Confirm that the command, working directory, resource use, and expected duration are already authorized. Use an absolute executable path and do not put credentials or secret values in command arguments.

Run:

```bash
python3 <plugin-root>/scripts/supervisor.py \
  start --name <name> --cwd <absolute-cwd> \
  [--artifact <absolute-path>]... \
  -- <absolute-executable> <args>...
```

Resolve `<plugin-root>` as the directory two levels above this `SKILL.md`.
Do not assume a user name, home directory, marketplace cache path, or repository
clone location.

Add both `--heartbeat-path <absolute-path>` and `--stale-after <seconds>` only when the underlying task explicitly owns and updates that heartbeat. Do not infer health from GPU use, log content, or ordinary silence.

The worker starts in a new process session and atomically records its PID plus
Linux `/proc` start ticks before running the command. The returned registration
is durable and every inspection verifies both identity fields before treating
the process as active. Preserve its `job_id`. Full stdout and stderr remain in
the reported `combined.log` path and must not be copied into model context by
default. Terminal success or failure comes only from the worker's atomic
`result.json`, not from PID disappearance alone.

## Wait And Resume

Call `wait_event(job_id)` once. It blocks inside the host process until an unacknowledged `completed`, `failed`, `attention`, or `supervisor_error` event exists. Do not wrap it in a Goal, repeated `wait`, shell polling, Scheduled task, Stop hook, or another monitor.

When an event arrives:

1. Read the bounded event and inspect only the evidence needed for the already-authorized work.
2. Treat `attention` as a request to inspect, not proof of failure.
3. Continue the current task only within its existing authority.
4. Call `ack_event(job_id, event_id)` after consuming the event.

An event never grants authority to cancel, retry, restart, repair, reconfigure resources, or launch a later stage. Ask the user if one of those actions is needed and was not already authorized.

## Reconnect And Maintain

After App or MCP restart, use `list_jobs()` or `inspect_job(job_id)`. An unacknowledged disk event is returned immediately. Call `wait_event(job_id)` again only while the job is running; an acknowledged terminal job cannot produce another event.

If the user steers or cancels a wait, leave the job unchanged. Reconnect later with `inspect_job` or `wait_event`.

If an MCP call returns `Transport closed`, do not loop in the same task. The current Codex App task does not restart that dead transport. Start a fresh task or restart the App, then call `list_jobs()` or `inspect_job(job_id)` to recover from disk.

Use the CLI equivalents only when MCP is unavailable:

```text
<plugin-root>/scripts/supervisor.py list
<plugin-root>/scripts/supervisor.py status JOB_ID
<plugin-root>/scripts/supervisor.py ack JOB_ID EVENT_ID
<plugin-root>/scripts/supervisor.py clean JOB_ID
```

`clean` removes only an inactive registration after a `completed`, `failed`, or
`supervisor_error` event has been acknowledged. PID disappearance alone is not
a terminal event. No interface in this plugin cancels, retries, restarts,
signals, or changes an underlying process.
