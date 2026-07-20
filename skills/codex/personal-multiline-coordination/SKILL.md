---
name: personal-multiline-coordination
description: Coordinate persistent Codex App tasks, isolated Git worktrees, cross-line intake, and explicitly authorized active-monitoring tasks; use implicitly only for read-only ownership reconciliation when existing tasks or worktrees are ambiguous.
---

# Personal Multiline Coordination

Coordinate durable lines that need their own Codex App task, worktree, or
recurring observation lifecycle. Use `personal-subagent-boundaries` for bounded
one-shot work.

The main process is the control plane. It owns decomposition, authority,
cross-line decisions, intake, and the final synthesis. App tasks perform
substantive line work or dedicated monitoring and stop at their assigned
boundary.

## Establish Authority

An explicit request for persistent or multiline execution authorizes only the
named non-destructive App tasks and worktrees. Ask separately before heavy or
long job launch, active monitoring, Git mutations, cleanup, publication, or an
external action unless the user already granted that exact action.

When this skill triggers because existing task or worktree ownership is
ambiguous, inspect read-only state and report it. Do not create, resume, move,
or archive tasks; create or remove worktrees; or write coordination state
without explicit execution authority.

Do not silently replace a requested App task with a managed subagent or local
main-process execution. If the required App surface is unavailable, report the
capability gap and preserve the intended line.

## Keep Minimal Line State

Keep line state in the current controller task unless the user explicitly asks
for a durable project record. Use prose, bullets, or a small table. Record only
what is needed to reproduce and coordinate the line:

- line ID and exact App task ID;
- goal and stop condition;
- canonical `cwd`, and worktree/branch when applicable;
- read boundary and exclusive write boundary;
- dependencies, current state, next wake event, and latest evidence.

Do not create a registry, schema snapshot, audit ledger, or project planning
file merely because work persists across turns. Native App task state, Git
state, and the controller's compact record are the evidence sources.

## Launch Persistent Lines

1. Inspect the repository root, applicable instructions, branch, worktrees,
   dirty state, in-progress Git operations, and overlapping user work.
2. Separate lines by dependencies and complete mutation surfaces. Never run
   concurrent writers over the same paths, generated outputs, caches, ports,
   data, or external mutable resource.
3. Resolve each ready writer's base and canonical worktree. Prefer an explicit
   path or repository convention; otherwise use an App-native or repo-sibling
   location outside the repository and `~/.codex`.
4. Create one user-visible App task per persistent line only within the
   explicit request. Give it the minimal line contract and an immutable
   `cwd`/worktree. Do not redirect a live writer to another worktree.
5. Leave the line to run independently. Do not make the controller poll or wait
   for routine progress. On a native completion/attention event or later intake,
   inspect the line's reported evidence, current diff/artifact, ownership, and
   freshness before deciding whether to accept it, request more evidence, or
   unblock another line.

Workers may give evidence-supported recommendations, but they do not decide
their own acceptance or authorize another stage. They do not stage, commit,
push, integrate, publish, repair another line, or clean resources unless that
exact mutation was separately authorized and assigned.

For integration, the controller first accepts an exact source state and then
assigns one owner for the exact integration mutation. Preserve source and
resulting commit identities. Stop on a conflict that needs a new design or
ownership decision. Final local completion still goes through
`personal-risk-verification`; a later Git outcome goes through its owning
workflow.

## One-Shot Status Is Not Monitoring

An ordinary status or ETA request authorizes one bounded read-only check by the
main process against the exact named job and evidence surface. Report observed
progress, evidence time or artifact identity, and uncertainty, then stop. Do
not create a task, recur, tail continuously, or infer an ETA that the evidence
does not support.

## Active Monitoring

Start active monitoring only after the user explicitly authorizes recurring
observation of one exact job and phase. Observation authority does not include
job launch, termination, repair, restart, output mutation, resource changes,
next-stage launch, or go/no-go decisions.

Before launch, freeze the monitoring contract: owner, exact job and phase
identity, evidence surfaces, progress and terminal signals, expected duration,
cadence, observation limits, retry budget, stop condition, and whether the
parent discussion task participates. Choose a cadence that matches the job.
When there is no better job-specific basis, check short jobs every 30-60
minutes; check multi-hour jobs first after 45-60 minutes and then every 90-120
minutes when stable; check overnight or multi-day jobs every 2-4 hours when
stable. Change the cadence only from fresh evidence or a new user instruction.

### Use A Monitoring App Task By Default

After the executor launches the detached job and completes its bounded startup
guard, create a dedicated monitoring App task on the same execution host. Use
model `gpt-5.6-luna` with low reasoning effort and confirm the task, model,
effort, host, exact job binding, and start signal are product-visible. Do not
replace this task with a managed subagent.

Reuse the former monitoring-subagent control flow inside the App task: keep its
turn active, perform a long sleep until the next sparse cadence checkpoint,
make one bounded read-only observation, and return to long sleep when no event
is present. Do not finish after the first observation, use short recurring
internal waits, or make the controller poll. Report only an agreed milestone,
`action_needed`, `failed`, `completed`, `preapproved_next_ready`, or a status
event requested by the user.

The monitoring task may write only the compact task-owned monitoring records
named in its contract. It must not stop, restart, repair, mutate outputs, launch
the next stage, publish, or make a go/no-go decision. The controller owns event
intake and every consequential action.

If the monitoring App task cannot be created on the execution host, cannot
remain active across its long sleep, or cannot bind the required evidence
surface, report `monitoring_unavailable`. If it exits, becomes idle, misses a
report beyond tolerance, or loses its binding before a terminal signal, report
`monitoring_interrupted`. Do not silently replace it or make the controller
poll.

### Keep Executor Automation As A Future Upgrade

Executor-owned in-chat heartbeat automation is a future upgrade path. Use it
only after the remote execution task itself exposes the automation tool and an
actual same-thread wake has been verified on that host. A local Scheduled task
that monitors a remote job over SSH is not the default fallback; it requires an
explicit user choice plus a frozen host identity, non-interactive SSH route,
exact read-only command allowlist, and remote job contract.

### Gate User-Visible Updates

A wait timeout is not a monitoring checkpoint or a user-visible event. Emit a
monitoring update only when the agreed cadence is due, a meaningful state change
or terminal event is observed, or the user asks. Process liveness, no new output,
and absence of an anomaly do not justify separate heartbeat messages.

At a cadence checkpoint, combine the useful state into one update: observation
time, exact job identity, cumulative progress and percentage when available,
progress since the prior checkpoint, retry state and remaining budget,
validation or telemetry anomalies, and the next checkpoint. If the user changes
the cadence, acknowledge it once, reset the next report time from that
instruction, and keep intervening internal waits silent.

### Include GPU Evidence

For every GPU-backed long-running job under active monitoring, include GPU
underutilization detection in the same monitoring-task contract. Do not create
a second GPU-only task. Bind the exact GPU devices and job processes,
expected GPU-active phases, explicitly expected low-utilization phases, and at
least one progress signal. Omit this evidence surface only when telemetry is
unavailable, the current phase is explicitly CPU-only, or the user explicitly
excludes it. Use the host-documented read-only telemetry surface. Never infer
persistent underutilization from one snapshot.

Unless job-specific evidence supports another contract, use this sparse GPU
profile:

- use the general 30-60 minute, 45-60 then 90-120 minute, or 2-4 hour cadence
  according to the expected job duration and observed stability;
- at each observation, collect a bounded 60-second window at 5-second intervals
  and record per-device utilization distribution, memory/process binding, and
  progress evidence;
- report `suspected_gpu_underutilization` only when the bound job remains alive
  and GPU-resident, utilization has median below 10% and p90 below 20% in two
  consecutive windows, and the bound progress signal is stale across the same
  interval; and
- distinguish whole-job low utilization from one-device imbalance, and exclude
  declared preprocessing, evaluation, checkpoint, and phase-transition windows.

If telemetry cannot bind the process to the devices, a required progress signal
is unavailable, or an expected low-utilization phase is ambiguous, report the
evidence gap instead of classifying the job as healthy or anomalous. The event
is observation evidence only; it never authorizes repair, restart, termination,
resource changes, or a go/no-go decision.

The monitoring task's read-only restriction is a semantic task boundary. It may
read only the named process/session, log, status, and output evidence. It must
never mutate the job or artifacts, send control signals, diagnose by changing
state, execute a contingency, decide success, or advance a phase. Each event
reports the exact evidence identity, observed transition, and uncertainty.

Treat monitoring-task liveness as part of the contract. If the task does not
start, exits unexpectedly, becomes idle before a terminal signal, cannot read a
required surface, or misses a report beyond the declared tolerance, fail closed
with `monitoring_unavailable` or `monitoring_interrupted` and wait for the user.
Do not silently create a replacement or make the controller poll.

On a terminal job signal, phase change, authorization withdrawal, or monitoring
boundary failure, the monitoring task reports its last evidence and stops. The
main process performs intake only after a native task
event or an explicit user request and alone decides what the evidence means and
whether any separately authorized action should follow.

## Recovery And Closeout

Reconcile exact App task and Git/worktree evidence before recovery. Preserve
dirty or ambiguous state. Do not restart a silent worker, abort a Git
operation, force-remove a worktree, delete a branch, prune globally, archive a
task, or discard output without exact authority and ownership.

Return the smallest useful handoff: current lines, accepted evidence,
unresolved ownership or dependencies, preserved worktrees/jobs, and the event
or decision needed next.

See [source notes](references/source-notes.md) only when maintaining this
skill's provenance or its locked monitoring preferences.
