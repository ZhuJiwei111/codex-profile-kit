---
name: personal-monitor-external-jobs
description: Use when the user explicitly asks to monitor or audit monitoring, or when an already-authorized external job or exact multi-stage pipeline will outlive its owning turn and needs repeated observation; select and prove a low-cost continuation topology, then establish or diagnose read-only supervision through terminal state, blocker, or a user-owned decision.
---

# Personal Monitor External Jobs

Observe one exact authorized job or pre-authorized pipeline. Never turn
observation into authority to start, restart, repair, retry, cancel, terminate,
reconfigure, clean up, or submit follow-up work.

## Activate At The Launch Boundary

Invoke for an authorized job that will outlive its owning turn, for a request to
monitor an existing job, or to audit whether claimed monitoring is still live.
Do not invoke for a short foreground command, a hypothetical or unauthorized
job, or a job whose owner will see the terminal result in the same turn.

Monitoring belongs to the launch contract, but this skill grants observation
only. Job launch, task creation or mutation, scheduling, and messages still
require their matching authority.

## Select A Continuation Topology

Separate three roles:

1. a sampler reads exact, cheap status sources;
2. a scheduler or attached live turn causes the next sample; and
3. an evaluator classifies evidence and reports meaningful events.

Choose topology from verified capabilities, not project identity or host names:

- **Scheduled evaluator:** one scheduled task can reach the status sources and
  perform one sample and decision per invocation.
- **Scheduled relay:** a scheduled controller requests one nonce-bound sample
  from an exact one-shot sampler, then evaluates the fresh response. Controller
  and sampler may run on the same or different execution hosts.
- **Attached live turn:** one dedicated low-cost task keeps the same turn alive
  through `foreground wait -> sample -> evaluate -> foreground wait` cycles.

Prefer a product-visible scheduled topology when available. A task is a context
container, not automatically a scheduler. A detached process, background loop,
growing monitor file, task final message, or task-wait API cannot by itself wake
an idle evaluator.

For scheduled topology, verify one immutable recurrence identity, exact target,
cadence and next wake, execution-host access to required sources, unattended
permissions, and event-delivery path. A creation receipt proves only
`establishing`; require one scheduler-triggered proof run before `established`.

For a relay, test the route manually and again in the first scheduled run. Send
one contract revision and unique nonce. Accept only a fresh response containing
that nonce, authoritative sampler identity, job identity, observation time,
event key, and bounded evidence. Reject old final messages, mismatched identity,
and responses outside the delivery grace. The sampler owns no recurrence,
repair authority, or independent monitor state.

For an attached live turn, first prove that one foreground wait can cover the
real cadence without periodic model re-entry. Observe one full `wait -> sample
-> decision -> next wait` cycle and confirm the same turn remains in progress.
A yielded shell session that needs repeated model turns to poll is not this
topology. Do not approximate a long cadence with many short inference cycles.

If no topology qualifies, take at most one authorized reconciliation sample and
report `not_established`, the missing capability, and the evidence that remains
unobserved. Keep supervision state separate from job health.

## Freeze A Parameterized Observation Contract

Record before handoff:

- immutable scheduler/job/run identity, or PID plus start time;
- execution host, cwd, runtime, argv, owner, controller/evaluator, and sampler;
- stages and exact transition gates;
- canonical state, receipt, bounded log, and expected artifact sources;
- cheap progress signals, success/failure, stall evidence, and interruption;
- sample/report cadence, unchanged backoff, stall window, delivery grace, and
  last successful sample time;
- required machine, app, mount, network, credential, and path availability;
- recurrence identity, target, next-wake requirement, and terminal disposition;
  and
- for a relay, message route, revision, nonce/freshness rules, timeout, and
  authoritative response fields.

Use values supplied and verified for the current job. Do not embed one
project's paths, identifiers, hashes, stages, thresholds, or artifact schema as
defaults for another project. Treat titles, process names, and self-reported IDs
as hints until verified against task, scheduler, process, or receipt evidence.
Record launch-time source or manifest hashes when they bind identity, but do not
claim later source drift changed code already loaded by a process.

For a pipeline, define each stage and the terminal evidence authorizing the next
stage. Extending coverage is a contract revision: supersede the prior contract,
sample affected stages, and acknowledge the revision before claiming coverage.

## Establish One Monitor Idempotently

Treat task-creation timeouts, interrupted calls, and contradictory errors as
ambiguous. Reconcile existing tasks and recurrences before retrying. Do not
create a duplicate while a possible matching monitor exists. Stop or archive a
duplicate only with matching task-management authority.

Accept a handoff only after the monitor:

1. acknowledges the exact contract and verified identities;
2. returns one successful fresh status sample; and
3. proves its continuation topology, including a next wake or next attached
   foreground wait.

Use these supervision states:

- `establishing`: contract exists; proof run is incomplete;
- `established`: proof run, fresh sample, and next continuation are verified;
- `not_established`: no qualifying continuation exists;
- `lost`: previously established continuation or identity is invalid; and
- `stopped`: a validated observation stop condition occurred.

Never use job `active`/`healthy`, a running sampler, or a creation receipt as a
synonym for `established`. An evaluator may be idle between verified scheduled
runs; an attached-turn monitor may not. After establishment, the owner does not
duplicate routine polling.

## Sample Cheaply And Report Events

Choose cadence from expected evidence rate and observation cost. Each scheduled
invocation performs exactly one fresh sample and decision. A relay requests at
most one one-shot sample per invocation.

- Read exact paths and bounded status fields during normal running.
- Aggregate byte counts, mtimes, CPU/I/O, child activity, and active-unit
  rotation as liveness evidence.
- Define an event key from stage, canonical status, completed/result count,
  active-unit set, failure set, identity state, and terminal state.
- Report terminal, failure, blocker, identity loss, stage transition, or user
  decision immediately.
- Report ordinary progress only when the event key changes or the agreed report
  interval elapses. Rate-limit liveness-only digests.
- Back off after unchanged healthy samples and reset after a real event.
- Verify recurrence and next wake on every scheduled invocation, or verify that
  the same attached turn owns the next foreground wait.

Do not copy growing logs, recursively scan broad trees, or repeatedly hash large
artifacts. Use cheap liveness checks while running, bounded diagnostics when
needed, and full receipt validation once at a candidate terminal state.

## Diagnose Conservatively

An unchanged state or quiet log is not a stall. Respect buffering and stages
where future state or artifacts are expected to be absent. Report a reproducible
blocker only after the contract's stall window plus corroborating evidence such
as no process/child, no CPU or I/O, no artifact growth, or a lost status source.
Otherwise report `suspected_stall` and return the decision to the owner.

Do not treat a stale summary as terminal while the immutable owner is alive or
a documented transition is running. Validate the old stage's terminal gate
before interpreting the next stage's absent or new state.

## Stop And Hand Back

Stop on validated terminal success/failure, reproducible blocker, identity or
status-source loss, explicit interruption, or a user-owned decision. Report the
observation time and exact evidence. Hand repair, retry, cancellation, cleanup,
and follow-up work back to the owner under separate authority.

Mark supervision `lost` if recurrence, attached turn, target binding,
execution-host access, identity, relay freshness, delivery grace, or next wake
fails—even if the job remains healthy. At a terminal condition, validate the
evidence before `stopped`. Pause or disable recurrence only with matching
authority; otherwise report schedule cleanup as an owner action and avoid new
sampling after the stopped contract.
