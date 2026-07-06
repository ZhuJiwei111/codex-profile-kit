---
name: personal-subagent-boundaries
description: Use when the user asks for subagents or when independent exploration, review, validation, or isolated implementation could be delegated.
---

# Personal Subagent Boundaries

Delegate only when isolation improves speed or quality. Main owns scope,
integration, stdout/stderr, and final verification.

## Before Delegating

Define objective, output, mode, exclusive files, stop condition, and report
format.

Require key paths, evidence, conclusions, risks, and next steps.

For Codex worker threads, multiple git worktrees, long-lived worker goals,
coordinator intake, or worktree archive/restart, also use
`personal-multiline-coordination`. Keep this skill focused on delegation,
subAgent ownership, and monitoring boundaries.

## Allowed Patterns

- Read-only exploration, comparison, or review.
- Isolated implementation with exclusive files.
- Validation against a specific artifact or command.

## Report and Reuse

Do not duplicate delegated observation locally. If the report is specific, use
it instead of re-reading the same files or rerunning the same exploration.

Do spot-check only when paths/evidence are missing, findings conflict,
or write integration, safety, credentials, final verification, or user request
requires it.

Do not say the subagent conclusion matches local observation unless an
independent check was done. Say you used the report or spot-checked one item.

## Hard Boundaries

- Do not allow concurrent edits to the same file, module, schema, config, report,
  plan, `AGENTS.md`, shared context, or sync file.
- Editing subagents must report changed paths and verification run.
- Do not create watcher subagents for long-running jobs by default.
- If the user asks for status, do one read-only check; do not start continuous
  monitoring unless explicitly requested for the current stage.
- Status checks must not mutate files, stop jobs, publish, clean artifacts, or
  make go/no-go decisions.
- Keep critical-path work local when delegation would block progress, couple
  files unsafely, or require unbounded context.

## Long-Running Monitoring

Default to no watcher subAgent for long-running jobs. Launch detached, run only
a bounded startup guard, hand off, and end the turn unless the user explicitly
authorizes active monitoring for the current stage.

The main process may perform a read-only startup guard without separate
active-monitoring authorization. Cap it at 10 minutes total. Use it only for
startup validation: process/session liveness, log creation, output directory
writability, expected first progress signal, and a few bounded GPU/status
samples when relevant. If the startup guard finds immediate failure, missing
launch evidence, no first progress signal after warmup, resource errors, or
unexplained GPU abnormalities, report the anomaly instead of silently extending
the guard.

Only after the user explicitly authorizes active monitoring for the current
stage may the main process create a monitoring subAgent. The main process then
becomes a persistent supervisor and uses repeat long wait: use the longest
available sleep/wait for monitoring events, and if no event arrives before a
wait timeout, continue waiting without reading logs, polling artifacts, querying
GPU status, or taking over monitoring.

Before delegating monitoring, define an inline monitoring contract with:
`job_id`, `phase`, `permission_scope`, `cwd`, `command`, `session_or_pid`,
`log_path`, `output_path`, `expected_artifacts`, `startup_guard_result`,
`health_signals`, `job_specific_thresholds`, `fallback_thresholds`, `cadence`,
`record_path`, `event_triggers`, `read_only_diagnostics`, `forbidden_actions`,
`stop_or_timeout_condition`, `report_format`, and `preapproved_next_actions`.

Prefer job-specific health signals and thresholds whenever the command,
framework, logs, or plan make them knowable. If the contract does not define a
relevant threshold, the monitoring subAgent must apply conservative fallback
checks for process/session anomalies, stalled progress, GPU anomalies, resource
pressure, error signals, and result or metric anomalies.

The default record path is project-local `.codex/monitoring/<job-id>/`, with
compact state in `monitor_status.json` and a short report in
`monitor_report.md`. `monitor_status.json` must include `job_id`, `phase`,
`permission_scope`, `status`, `updated_at`, `cwd`, `command`, `session_or_pid`,
`log_path`, `output_path`, `latest_check`, `progress`, `eta`, `signals`,
`stop_reason`, and `next_safe_action`. Do not copy long logs or secrets.

Use estimate cadence instead of a fixed cadence. Estimate total runtime, first
visible progress point, early failure window, log or artifact update frequency,
and next-stage trigger condition. Defaults are intentionally sparse: short tasks
check every 30-60 minutes; multi-hour tasks first check after 45-60 minutes and
back off to 90-120 minutes when stable; overnight or multi-day tasks back off to
every 2-4 hours when stable. Shorten the first check only for high early failure
risk, then back off after stability is established.

Cadence is not a reason to ignore anomalies. At each check, compare evidence
against job-specific thresholds first, then fallback thresholds. Return an
`action_needed` event with a compact read-only diagnostic summary when an
anomaly is detected.

Fallback anomalies include:

- Process/session anomalies: missing tmux session or PID, defunct process,
  command mismatch, target child exit, or live wrapper with missing worker.
- Stalled progress: no log growth, no step/epoch/sample progress, unchanged
  expected artifacts or checkpoints, missing first artifact after warmup, or an
  unsupported ETA.
- GPU anomalies: sustained low utilization after warmup, unexplained 0-100
  utilization thrashing, wrong or missing expected device use, multi-device
  imbalance only when the contract expects balanced devices, and GPU memory or
  CUDA errors. Non-target processes on the same GPU are background context only
  and must not trigger an anomaly by themselves.
- Resource pressure: low disk space or inodes, RAM or swap pressure, insufficient
  `/dev/shm`, high IO wait explaining a stall, write-permission failures, or
  filesystem errors.
- Error signals: repeated or fatal OOM, CUDA/NCCL failures, segmentation faults,
  tracebacks, data loader errors, permission denied, no space left, connection
  reset, or missing input data.
- Result or metric anomalies: `nan` or `inf` metrics, sudden throughput
  collapse, ETA regression without progress explanation, zero-byte checkpoints,
  or outputs stuck as temporary or partial files.

monitoring subAgent only is a read-only observer. It may inspect status and
write compact monitoring records, but it must not stop, restart, repair, launch
the next stage, publish, clean artifacts, mutate training outputs, or make
go/no-go decisions. It normally updates the agreed record path and sleeps. It
returns a short event summary only for `action_needed`, `failed`, `completed`,
`preapproved_next_ready`, or an agreed milestone.

Use `action_needed` for anomalies that require user or supervisor judgment,
`failed` only when failure is directly evidenced by process exit, fatal logs, or
contract-defined failure markers, `completed` only when the completion condition
is evidenced, and `preapproved_next_ready` only when the contract's preapproved
next-step trigger is satisfied.

Other subagents, including explorer, worker, editing, and validation subAgents,
are not constrained by the monitoring read-only rule. They may still run
commands, edit exclusive files, implement tasks, and run verification according
to their delegated ownership.

Monitoring should use low reasoning only. If the runtime supports
`reasoning_effort`, set it to `low`; otherwise use `lowest available reasoning effort`.
Do not change reasoning effort for ordinary subAgents, and do not switch the
monitoring model unless the user explicitly asks.

When the main process receives a monitoring event, it may repair, restart, or
launch the next step only if that action was preapproved in the plan. Ask the
user first for actions that are not preapproved or that affect cost, resources,
data safety, environment configuration, or scope.
