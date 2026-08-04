---
name: personal-monitor-external-jobs
description: Use when the user explicitly asks to monitor, establish monitoring, or audit monitoring for an exact authorized external job or pipeline; keep short simple observation in the owner task, and register low-cost read-only Scheduled or live monitoring for work that will outlive the owner turn.
---

# Personal Monitor External Jobs

Observe one exact authorized job or pre-authorized pipeline. Monitoring never
grants authority to launch, restart, repair, retry, cancel, terminate,
reconfigure, clean up, or submit follow-up work.

## Choose The Short Or Long Path

Estimate the remaining observation time before choosing a mechanism.

- If the expected remainder is 10 minutes or less and each check is simple, the
  owner task may monitor directly.
- If the expected remainder is longer than 10 minutes or unknown, register an
  isolated monitor. The owner task must not stay attached for routine polling.

Before creating a long monitor, finish all safe read-only preflight and present
one question card without auto-resolution. Ask the user to approve one
standalone Scheduled registration at the proposed cadence and pre-authorize one
live-task fallback if registration fails. Silence or UI expiry grants neither
choice.

Record the smallest complete observation contract:

- owner task ID and host ID;
- immutable job, run, scheduler identity, or PID plus start time;
- target host, cwd, runtime, and exact status sources;
- cheap progress evidence, terminal success/failure evidence, stall evidence,
  and identity-loss signals;
- expected remaining-time bucket and proposed sample cadence; and
- the exact recurrence or live task created for this contract.

Use only values verified for the current job. Never embed a concrete host,
port, project path, job ID, stage name, threshold, or artifact layout as a
portable default.

## Resolve The Local Controller And SSH Alias

Run long Scheduled monitoring from the local controller. Read and maintain that
controller's own `~/.codex/HOST_LOCAL.md`; do not write local-controller facts
into a remote host's overlay or the portable profile.

Inventory only remote hosts saved or discovered by Codex. For each relevant
host, record a non-secret snapshot containing:

- Codex host ID or project label mapped to one SSH alias;
- effective hostname, port, and user from filtered `ssh -G <alias>` output;
- a non-secret proxy alias or route description when applicable;
- relevant saved project roots; and
- the result and timestamp of a bounded unattended probe using
  `BatchMode=yes`.

Never record or expose credentials, private-key contents, tokens, auth-agent or
socket state, or a secret-bearing proxy command. Treat the resolved hostname
and port as audit metadata only. Start monitoring connections with
`ssh <alias>` and append only the exact read-only remote command, so the user's
SSH configuration remains authoritative. Re-resolve the alias and repeat a
bounded read-only probe whenever monitoring is registered.

If the local controller cannot reach the exact target directly, treat
Scheduled registration as failed and use the authorized live-task fallback.
Do not invent an intermediate host or durable forwarding process.

## Register One Monitor

Inspect the callable scheduling and task-management capabilities before using
them. Reconcile exact matching recurrences and tasks before every create retry;
creation timeouts and interrupted calls are ambiguous, not proof of absence.

Prefer one standalone Scheduled task. Configure each scheduled invocation so
that it performs one bounded fresh sample and exits. It must not sleep, loop,
start a watcher, copy a growing log, recursively scan broad trees, or control
the external job. Choose the cheapest cadence consistent with the evidence
rate. Dynamically select the lowest-cost available model known to support the
required tools, with low reasoning; if capability or cost is not exposed, keep
the destination default rather than guessing.

Scheduled registration succeeds when the product returns a stable schedule ID
and, when inspection is supported, the same schedule reads back as enabled with
the expected target and cadence. Report this state as
`registered_unverified`. Do not wait for the first scheduled run, trigger a
proof invocation, or claim that the execution path has been proven.

The owner task may wait for the local setup task to return only this creation
result. Once it receives the stable ID, it stops monitoring work and can handle
other turns or remain idle. It must not run shell sleeps, retain a long-lived
polling command, or duplicate routine samples.

If registration fails or remains ambiguous, reconcile by the exact observation
contract, pause any matching partial recurrence, and create one isolated live
task on the exact target host. A stable thread ID is sufficient to report
`live_registered`; do not wait for its first sample. The dedicated live task
inherits the same read-only contract, cadence, and dynamic low-cost model policy
and monitors through terminal state, blocker, identity loss, or a user-owned
decision. It may use efficient foreground waits, but must not busy-poll. If
neither monitor can be registered, report the exact blocker without creating
duplicates.

## Handle Scheduled Runs

On each scheduled run, bind the fresh sample to the recorded job identity and
read only bounded authoritative status. An unchanged state or quiet log is not
a stall; require the agreed stall window plus corroborating process, CPU/I/O,
child-activity, or artifact evidence. Validate exact terminal evidence before
reporting success or failure.

- If the job is still normally running, exit without messaging the owner.
- On terminal success/failure, sampling failure, blocker, identity loss, or
  status-source loss, pause the exact recurrence before reporting.
- After successful registration, a run-time failure does not authorize
  automatic live-task fallback. Return recovery, resume, or fallback decisions
  to the user.

Queue one event to the owner task with observation time, monitor ID, job
identity, bounded evidence, pause result, and the required decision. Never
interrupt a running owner turn; enqueue the event after that turn. If delivery
is unavailable, leave the result visible in the Scheduled or live-task surface.
A scheduler failure that prevents the run from starting cannot self-report, so
the product's Scheduled view remains the fallback evidence source.

## Stop Without Archiving

At a validated terminal or attention condition, leave the exact recurrence
paused rather than deleting it. Do not archive the recurrence, Scheduled run,
local setup task, or live task, and do not ask an automatic archive question.
Archive only after a later explicit user request.

Local Scheduled tasks require the local computer to remain on, the Codex
desktop app to remain running, and required local projects to remain available.
The owner task may be idle; operating-system sleep suspends observation.
