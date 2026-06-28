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

Default to no watcher subAgent for long-running jobs. Launch detached, do one
read-only sanity check, hand off, and end the turn.

Only after the user explicitly authorizes active monitoring for the current
stage may the main process create a monitoring subAgent. The main process then
becomes a persistent supervisor and uses repeat long wait: use the longest
available sleep/wait for monitoring events, and if no event arrives before a
wait timeout, continue waiting without reading logs, polling artifacts, querying
GPU status, or taking over monitoring.

Before delegating monitoring, define: `job_id`, `phase`, `permission_scope`,
`cwd`, `command`, `session_or_pid`, `log_path`, `output_path`, `estimate
cadence`, `record path`, `event triggers`, `stop/timeout condition`, `report
format`, and any preapproved next actions.

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

monitoring subAgent only is a read-only observer. It may inspect status and
write compact monitoring records, but it must not stop, restart, repair, launch
the next stage, publish, clean artifacts, mutate training outputs, or make
go/no-go decisions. It normally updates the agreed record path and sleeps. It
returns a short event summary only for `action_needed`, `failed`, `completed`,
`preapproved_next_ready`, or an agreed milestone.

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
