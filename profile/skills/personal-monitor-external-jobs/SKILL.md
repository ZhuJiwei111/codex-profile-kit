---
name: personal-monitor-external-jobs
description: Manual only. Use only when the user explicitly invokes this skill to keep observing one already-authorized long-running external job until it reaches a terminal state, becomes blocked, or needs a user-owned decision.
---

# Personal Monitor External Jobs

Monitor one exact existing job without turning observation into authority to
restart, repair, cancel, relaunch, reconfigure, or submit another job.

## Fix The Observation Contract

Identify the job, status source, owning task or process, expected evidence,
terminal states, blocker signal, and any explicit interruption condition. Use
only the read-only checks and ordinary resource use already authorized.

Prefer a product-visible scheduled or monitoring App task when the available
tools can create one. Otherwise, poll from the job owner or a dedicated visible
monitoring task using bounded `sleep`/wait intervals and read-only status
checks.

Choose the interval from the expected rate of new evidence and the cost of the
check. Back off when repeated checks are unchanged; reset after a change.
Yield often enough for user input and product visibility rather than hiding a
long blocking wait.

## Report Only Meaningful Change

Do not send unchanged heartbeats or copy growing logs. Report a transition,
new result, blocker, terminal outcome, or required user action with the exact
evidence and observation time.

Stop on terminal success or failure, a reproducible blocker, loss of the agreed
status source, explicit interruption, or a decision that belongs to the user.
Hand repair or follow-up work back to the owning task under separate authority.
