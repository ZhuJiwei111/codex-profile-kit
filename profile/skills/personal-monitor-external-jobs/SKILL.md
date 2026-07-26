---
name: personal-monitor-external-jobs
description: Use when the user explicitly asks to monitor, or when one already-authorized external job is about to launch or is running and will outlive the owning turn or need repeated observation; establish read-only supervision through terminal state, blocker, or a user-owned decision.
---

# Personal Monitor External Jobs

Monitor one exact existing job without turning observation into authority to
restart, repair, cancel, relaunch, reconfigure, or submit another job.

## Activate At The Launch Boundary

Invoke implicitly for an already-authorized job that is expected to outlive the
owning turn or require repeated checks. Monitoring is part of that job's launch
contract, not a later cleanup step. Do not invoke for a short foreground command,
an unauthorized or hypothetical job, or a job whose existing owner will observe
its terminal result in the same turn.

This skill grants observation only. Job launch, App-task creation, scheduling,
messages, and other external changes still require their matching authority.

## Fix The Observation Contract

Record the exact host, scheduler/job/run identity, start time, working
directory, executable or runtime, owning task, expected artifacts, canonical
status and log or receipt sources, progress signal, terminal states, stall or
blocker signal, and any explicit interruption condition. Prefer an immutable
job ID or PID plus start time over a bare process name or PID.

Use absolute host-recorded runtimes and paths where they matter. Use only the
read-only checks and ordinary resource use already authorized.

## Establish And Hand Off

Prefer a product-visible scheduled or monitoring App task when the tools and
task-creation authority are available. Otherwise, keep observation in the owner
only when the user asked that task to monitor; if neither route is authorized,
say that independent supervision is not established and request the needed
choice at the launch boundary.

A handoff is not established merely because a task or polling loop was started.
The monitor must acknowledge the exact observation contract and return one
successful initial status sample. The owner may claim that monitoring is active
only after that handshake.

Poll using bounded `sleep` or wait intervals and read-only status checks. Choose
the interval from the expected rate of new evidence and the cost of the check.
Back off when repeated checks are unchanged; reset after a change. Yield often
enough for user input and product visibility rather than hiding a long blocking
wait. The owning discussion task does not duplicate routine polling after a
dedicated monitor has acknowledged the job.

## Report Only Meaningful Change

Do not send unchanged heartbeats or copy growing logs. Report a transition,
new result, blocker, terminal outcome, or required user action with the exact
evidence and observation time.

Stop on terminal success or failure, a reproducible blocker, loss of the agreed
status source, explicit interruption, or a decision that belongs to the user.
Hand repair or follow-up work back to the owning task under separate authority.
