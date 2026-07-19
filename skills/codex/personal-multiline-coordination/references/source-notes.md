# Source Notes

Checked: 2026-07-19.

This is a local-origin workflow shaped by recurring Codex App task, Git
worktree, long-job, and recovery use. No external workflow text or executable
is bundled.

Key local preferences are a main-process control plane, one immutable worktree
per persistent writer, minimal in-conversation line state, event-driven intake,
and preservation-first recovery. Active monitoring is explicit only. The
executor that launches a long-running job owns its waiting and monitoring, with
an in-chat Scheduled task preferred for wakeups. This supersedes the former
dedicated-observer default. Consecutive internal waits are a silent executor
fallback when scheduling is unavailable; their timeouts are neither monitoring
checkpoints nor user-visible events. The parent discussion task does not poll.

A dedicated observer remains available only for an external or otherwise
unowned job. It requires a product-visible in-chat schedule, requests
`gpt-5.6-luna` with low reasoning, stays read-only, and fails closed rather than
falling back to a one-turn observer, another model, a managed subagent, or
controller polling. Without a better job-specific basis, cadence uses
`20 -> 40 -> 60 -> 60 ...` minutes. Cadence updates reset the next report time;
visible reports are gated on the agreed checkpoint, a meaningful state change,
a terminal event, or a user request.

Active monitoring for every GPU-backed long-running job includes
underutilization detection in the same monitoring owner by default. The locked
balanced profile uses short bounded telemetry windows at sparse adaptive
intervals, requires two low-utilization windows plus stale progress before
reporting a suspected anomaly, and treats expected low-utilization phases and
missing process/device evidence as uncertainty rather than failure.
