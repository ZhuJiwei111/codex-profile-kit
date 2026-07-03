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
`tmux` or `nohup`, state the Plan vs Actual mapping, estimate runtime, do at
most one read-only sanity check, then hand off the command, cwd, environment,
tmux session or process id, logs, outputs, one status-check command, expected
artifacts, and success/failure signals.

The main process should not directly use `watch`, `tail -f`, `nvidia-smi -l`,
`while true`, repeated polling, artifact polling, repeated log reads, GPU status
loops, or a long terminal observation loop for long-running monitoring.

Goal continuation is also not a monitoring cadence. If a worker goal starts a
long GPU job, download, eval, or batch process, keep the goal for the bounded
stage but switch observation to detached execution plus a monitoring subAgent.
The worker should wait for monitor events instead of repeatedly waking itself
to check progress.

Only continue with active monitoring when the user explicitly authorized it for
the current stage. In that case, spawn a monitoring subAgent and keep the main
process alive as a persistent supervisor. The main process should use repeat
long wait: run the longest available sleep/wait for monitoring subAgent events;
if a wait times out with no event, continue waiting without taking over
monitoring.

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

Default records go under `.codex/monitoring/<job-id>/` as
`monitor_status.json` and `monitor_report.md`; do not copy long logs or
secrets. The subAgent should return a short event summary only for
`action_needed`, `failed`, `completed`, `preapproved_next_ready`, or an agreed
milestone.

Without that current-stage authorization, end the turn and wait for the user to
return after completion for result inspection or analysis.
