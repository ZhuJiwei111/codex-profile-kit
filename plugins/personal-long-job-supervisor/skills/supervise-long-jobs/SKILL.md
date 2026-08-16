---
name: supervise-long-jobs
description: Launch and supervise an already-authorized non-interactive Linux command expected to run longer than about ten minutes when the current Codex task should resume after completion, failure, or a declared health condition. Use detached worker-side observation instead of model polling, Scheduled tasks, Stop hooks, or ad hoc terminals. Also use to discover monitor capabilities, reconnect to, acknowledge, or clean registrations created by this supervisor. Do not use for interactive commands, short commands, unauthorized resource use, experiment orchestration, or automatic cancellation, retry, restart, signaling, or reconfiguration.
---

# Supervise Long Jobs

Keep execution, sampling, and logs in the detached worker. Return to the model only for a durable event.

## Choose The Observation Contract

Resolve `<plugin-root>` as the directory two levels above this `SKILL.md`. Do not assume a home directory, clone path, mount, container layout, GPU index, or marketplace cache path.

Call `get_capabilities()` before selecting health monitors. When MCP is unavailable, run:

```text
python3 <plugin-root>/scripts/supervisor.py capabilities
```

State one concise line before launch: `Observation contract: baseline + <monitors>`.

- Baseline PID/start-ticks identity and atomic terminal result are always active.
- For an ML job assigned NVIDIA GPUs, default to per-process-tree utilization below 5 percent for 15 minutes, with a 5-minute startup grace. Alert when any assigned GPU is continuously idle.
- For an ML output or artifact filesystem, default to available space below 5 percent or 20 GiB for 60 seconds.
- Add heartbeat only when the launched job explicitly owns and updates that path.

Derive GPU scope and filesystem paths from the authorized task and current capability result. If a context-aware default is unsupported, omit it and report the capability `evidence_gap`. If the user explicitly requires an unsupported monitor, stop before launch. Read [observation contract schemas](references/observation-contracts.md) when constructing monitor JSON.

## Launch

Confirm the command, working directory, resource use, and expected duration are already authorized. Use an absolute executable path and keep credentials out of command arguments.

```text
python3 <plugin-root>/scripts/supervisor.py \
  start --name <name> --cwd <absolute-cwd> \
  [--artifact <absolute-path>]... \
  [--monitor '<strict-json-object>']... \
  -- <absolute-executable> <args>...
```

The detached worker records its own identity, launches the target with `Popen`, records the target identity separately, and samples the declared monitors while the target runs. Preserve the returned `job_id`. Terminal success or failure comes from the atomic result record, never PID disappearance alone.

## Wait And Resume

Call `wait_event(job_id)` once. It blocks in the host process without model sampling until an unacknowledged `completed`, `failed`, `attention`, or `supervisor_error` exists. Do not wrap it in Goal polling, repeated waits, shell polling, a Scheduled task, or another monitor.

When an event arrives:

1. Treat `attention` as a request to diagnose, not proof of failure.
2. Use the bounded event and `inspect_job(job_id)` first. If evidence remains insufficient, read at most the final 8 KiB of the reported `combined.log`; do not ingest the whole log by default.
3. Repair only when the original task already authorized that exact class of change. The event itself grants no new authority.
4. Call `ack_event(job_id, event_id)` after consuming the event, then wait again only if the job remains active.

No event or interface authorizes automatic cancellation, retry, restart, signaling, GPU reassignment, parameter change, resource reconfiguration, or a later pipeline stage.

## Reconnect And Maintain

After App or MCP restart, use `list_jobs()` or `inspect_job(job_id)`. Worker-side health sampling continues while MCP is disconnected, and an unacknowledged disk event returns immediately after reconnect.

If a wait is steered or cancelled, the underlying job remains unchanged. If MCP reports `Transport closed`, move recovery to a fresh task instead of looping on the dead transport.

CLI fallbacks are:

```text
<plugin-root>/scripts/supervisor.py list
<plugin-root>/scripts/supervisor.py status JOB_ID
<plugin-root>/scripts/supervisor.py ack JOB_ID EVENT_ID
<plugin-root>/scripts/supervisor.py clean JOB_ID
```

`clean` removes only an inactive registration after a terminal or supervisor-error event has been acknowledged. It never sends a signal.
