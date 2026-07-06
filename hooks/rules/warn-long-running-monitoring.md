---
name: warn-long-running-monitoring
enabled: true
event: bash
action: warn
pattern: (?i)(\bwatch\s+|\btail\s+[^\n;|]*(--follow|-[a-z]*f[a-z]*)\b|\bnvidia-smi\b[^\n;|]*(-l(ms)?\b|--loop(-ms)?(\b|=))|\bwhile\s+(true|:)(\s|;|$))
---

Detected a command pattern commonly used for continuous monitoring.

Short tasks expected to finish within 10 minutes may be monitored or awaited to
completion. If this is a long-running job, prefer launching it detached with
`tmux` or `nohup`, state the Plan vs Actual mapping, estimate runtime, then run
only a bounded read-only startup guard. The startup guard is allowed by default
but must be capped at 10 minutes total. Use it for launch validation: process or
session liveness, log creation, output directory writability, expected first
progress signal, and a few bounded GPU/status samples when relevant.

If the startup guard finds immediate failure, missing launch evidence, no first
progress signal after warmup, resource errors, or unexplained GPU abnormalities,
report the anomaly instead of silently extending the guard. Without active
monitoring authorization, hand off the command, cwd, environment, tmux session
or process id, logs, outputs, one status-check command, expected artifacts,
startup guard result, and success/failure signals, then end the turn.

The main process should not directly use `watch`, `tail -f`, `nvidia-smi -l`,
`while true`, repeated polling, artifact polling, repeated log reads, GPU status
loops, or a long terminal observation loop for long-running monitoring.

Goal continuation is also not a monitoring cadence. If a worker goal starts a
long GPU job, download, eval, or batch process, keep the goal for the bounded
stage but switch observation to detached execution plus a monitoring subAgent.
The worker should wait for monitor events instead of repeatedly waking itself
to check progress.

Only continue with active monitoring when the user explicitly authorized it for
the current stage. In that case, define an inline monitoring contract, spawn a
monitoring subAgent, and keep the main process alive as a persistent supervisor.
The contract should include health signals, job-specific thresholds, fallback
thresholds, read-only diagnostics, event triggers, forbidden actions, record
path, report format, stop/timeout condition, and preapproved next actions. The
main process should use repeat long wait: run the longest available sleep/wait
for monitoring subAgent events; if a wait times out with no event, continue
waiting without taking over monitoring.

monitoring subAgent only is the read-only observer. It may inspect state and
write compact records, but it must not stop, restart, repair, launch the next
stage, publish, clean artifacts, mutate training outputs, or make go/no-go
decisions. Other subagents are not constrained by this monitoring read-only
rule and should follow their normal delegated ownership.

Monitoring should use low reasoning only. If the runtime supports
`reasoning_effort`, set it to `low`; otherwise use `lowest available reasoning effort`.
Do not change ordinary subAgent reasoning effort or switch models unless the
user explicitly asks.

Use dynamic sparse cadence: estimate cadence from total runtime, first visible
progress point, early failure window, log or artifact update frequency, and the
next-stage trigger. Defaults: short tasks every 30-60 minutes; multi-hour tasks
first check after 45-60 minutes and back off to 90-120 minutes; overnight or
multi-day tasks back off to every 2-4 hours. Shorten the first check only for
high early failure risk, then back off when stable.

Sparse cadence is not permission to hard-wait through anomalies. At every check,
the monitoring subAgent should compare evidence against job-specific thresholds
first, then fallback thresholds. Fallback anomalies include process/session
problems, stalled progress, GPU anomalies, resource pressure, error signals, and
result or metric anomalies. GPU fallback anomalies include sustained low
utilization after warmup, unexplained 0-100 utilization thrashing, wrong or
missing expected device use, multi-device imbalance only when the contract
expects balanced devices, and GPU memory or CUDA errors. Non-target processes on
the same GPU are background context only and should not trigger an anomaly by
themselves.

Default records go under `.codex/monitoring/<job-id>/` as
`monitor_status.json` and `monitor_report.md`; do not copy long logs or
secrets. The subAgent should return a short event summary only for
`action_needed`, `failed`, `completed`, `preapproved_next_ready`, or an agreed
milestone. Use `action_needed` for anomalies that require judgment, `failed`
only for evidenced failure, `completed` only for evidenced completion, and
`preapproved_next_ready` only for a contract-defined trigger.

Without that current-stage authorization, end the turn and wait for the user to
return after completion for result inspection or analysis.
