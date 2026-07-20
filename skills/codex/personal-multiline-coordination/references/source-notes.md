# Source Notes

Checked: 2026-07-20.

This is a local-origin workflow shaped by recurring Codex App task, Git
worktree, long-job, and recovery use. No external workflow text or executable
is bundled.

Key local preferences are a main-process control plane, one immutable worktree
per persistent writer, minimal in-conversation line state, event-driven intake,
and preservation-first recovery. Active monitoring is explicit only. A
dedicated, product-visible monitoring App task is the default after bounded
startup validation. It runs on the execution host with `gpt-5.6-luna` and low
reasoning, reuses the former monitoring-subagent long-sleep and sparse-check
control flow, and keeps the parent discussion task from polling.

Executor-owned in-chat automation is a future upgrade path only after the
remote task surface exposes it and a real same-thread wake is verified. A local
Scheduled task that observes a remote job over SSH requires an explicit user
choice and a frozen SSH/read-only command contract; it is not the default
fallback. The monitoring task stays read-only and fails closed rather than
falling back to a one-turn observer, managed subagent, short recurring waits,
or controller polling. Sparse cadence defaults to 30-60 minutes for short jobs,
45-60 then 90-120 minutes for multi-hour jobs, and 2-4 hours for overnight or
multi-day jobs.

Active monitoring for every GPU-backed long-running job includes
underutilization detection in the same monitoring owner by default. The locked
balanced profile uses short bounded telemetry windows at sparse adaptive
intervals, requires two low-utilization windows plus stale progress before
reporting a suspected anomaly, and treats expected low-utilization phases and
missing process/device evidence as uncertainty rather than failure.
