---
name: personal-monitor-external-jobs
description: Monitor or audit one exact authorized external job or pipeline; keep short observation in the owner task, and use one fixed local gpt-5.6-luna controller plus read-only Scheduled monitoring for longer work.
---

# Personal Monitor External Jobs

Observe one exact authorized job or pre-authorized pipeline. Monitoring never
grants authority to launch, restart, repair, retry, cancel, terminate,
reconfigure, clean up, or submit follow-up work.

## Choose The Short Or Long Path

- If the expected remainder is 10 minutes or less and each check is simple, the
  owner task may monitor directly.
- If the remainder is longer or unknown, use the fixed local monitoring
  controller and one Scheduled registration. The owner must not routine-poll.

An explicit request to monitor authorizes one Scheduled registration for the
exact observation contract. Finish safe read-only preflight first. Ask only for
required contract fields that cannot be discovered read-only. When a choice is
required, use one question card without auto-resolution that states the
proposed cadence and separately requests pre-authorization for one live-task
fallback plus narrow pause authority. Silence grants neither.

Record the smallest complete observation contract:

- owner task ID and host ID;
- immutable job, run, scheduler identity, or PID plus start time;
- target host, cwd, runtime, and exact status sources;
- cheap progress evidence, terminal success/failure evidence, stall evidence,
  and identity-loss signals;
- expected remaining-time bucket and proposed sample cadence; and
- the exact recurrence or live task created for this contract.

The only facts the owner may need to supply are the exact task identity, status
source, terminal evidence, stall evidence, expected remaining duration, and
cadence. Use only values verified for the current job. Never embed a concrete
host, port, project path, job ID, stage name, threshold, or artifact layout as
a portable default.

## Fix Controller Identity And Model

Reuse one fixed local monitoring controller for long jobs. Configure that task
as `gpt-5.6-luna` with `medium` reasoning. A heartbeat automation attached to
the controller inherits those settings; if the product exposes model fields on
a standalone schedule, set the same values explicitly. Do not silently select
another model or effort when Luna is unavailable; report the blocker.

Resolve every App task to a readable canonical thread ID before recording it.
A `clientThreadId` is not a canonical task ID. Reconcile creation receipts
through task listing/read APIs, and never put an unresolved creation ID into a
project plan or monitoring contract.

## Resolve The Local Controller And SSH Alias

Treat the controller's `~/.codex/HOST_LOCAL.md` as read-only input. Monitoring
authority never permits creating, editing, or refreshing it. Report missing or
stale required facts and request separate configuration authority.

Map the target host ID or project label to one SSH alias. Record only filtered
hostname, port, user, non-secret route facts, relevant project roots, and the
timestamp/result of a bounded unattended `BatchMode=yes` probe. Use filtered
`ssh -G <alias>` for audit evidence, but make actual connections with
`ssh <alias>`. Never expose credentials, keys, tokens, sockets, or a
secret-bearing proxy command.

## Register Or Update One Schedule

Inspect callable scheduling and task tools. Reconcile exact matching
recurrences before every create retry; creation timeouts and interrupted calls
are ambiguous, not proof of absence. Reuse one exact paused schedule only after
replacing its old owner, run identity, sources, terminal rules, and cadence with
the current observation contract.

Prefer one heartbeat automation attached to the fixed controller. Each
invocation performs one bounded fresh sample and exits: no sleep, loop, watcher,
growing-log copy, broad recursive scan, new task, or job control. Sample the
target directly through `ssh <alias>`; the controller must not relay routine
samples through a remote App task.

Keep hash algorithms and domains typed. A raw-file hash and a canonical content
self-hash are different evidence and must never be compared as if they were the
same identity field.

Scheduled registration succeeds when the product returns a stable schedule ID
and the same schedule reads back enabled with the exact controller target and
cadence. Report `registered_unverified`; Do not wait for the first scheduled
run or trigger a proof invocation. Once this readback succeeds, the owner stops
active polling and does not duplicate routine samples.

## Bound A Live Fallback

If registration fails or remains ambiguous, reconcile the exact contract.
Only when the owner explicitly pre-authorized both actions may the attempt pause
a partial recurrence and create one isolated live task on the exact target host.
Pause authority applies only to a recurrence that exactly matches the current
observation contract and was created by this registration attempt or discovered
as ambiguous during it; it never applies to historical, merely similar, or
unrelated recurrences.

Configure the fallback task as `gpt-5.6-luna` with `medium` reasoning and
resolve its canonical thread ID. A stable task ID alone is not enough. Require
one fresh initial sample plus a live continuation that can perform the next
bounded wait without another user turn or schedule. If the task becomes idle or
returns a final answer while the job is still running, monitoring is not
established. Never record a promise to sample later as supervision.

Without the required authority or continuation, report the blocker. A
run-time failure after successful registration does not authorize automatic
live-task fallback.

## Handle Runs And Stop

Bind every sample to the exact job identity and read only bounded authoritative
status. Quiet logs or unchanged state alone are not a stall; require the agreed
window plus corroborating process, CPU/I/O, child activity, or artifact
evidence.

- If the job is normally running, exit without messaging the owner.
- On terminal success/failure, sampling failure, blocker, identity loss, or
  source loss, pause the exact recurrence before reporting.
- Queue one event to the owner task with observation time, canonical monitor
  ID, job identity, bounded evidence, pause result, and required decision.
  Never interrupt a running owner turn.

If delivery fails, leave the event visible in the Scheduled or live-task
surface. Do not archive or delete the recurrence, Scheduled run, controller, or
fallback task. Archive only on a later explicit request. The local computer and
Codex app must remain running; operating-system sleep suspends observation.
