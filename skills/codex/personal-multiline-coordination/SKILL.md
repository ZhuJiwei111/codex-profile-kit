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
substantive line work and own the waiting and monitoring for long-running jobs
they launch. They stop at their assigned boundary.

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
When there is no better job-specific basis, use the fallback intervals
`20 -> 40 -> 60 -> 60 ...` minutes. Change the cadence only from fresh evidence
or a new user instruction.

### Prefer In-Chat Scheduling

The executor that launches a long-running job owns its waiting and monitoring.
When Scheduled-task capability is available, attach an in-chat Scheduled task
to that executor's existing chat. Do not use a standalone schedule that creates
a new chat for every run, and do not describe recurrence in an ordinary App-task
prompt as if that alone will wake the task.

Give the scheduled prompt the durable monitoring contract. Each run performs
one bounded observation against the exact evidence surfaces and reports only
through the commentary gate below. When a terminal signal or stop condition is
observed, report the final evidence and pause its schedule while retaining the
run history. Do not delete or archive the chat automatically.

If in-chat scheduling is unavailable, an executor monitoring its own job may
keep the current turn active and perform consecutive internal waits of no more
than 60 seconds. Keep those waits silent until the commentary gate opens.

Only create a dedicated observer for an external or otherwise unowned job. It
still requires explicit monitoring authority and a product-visible in-chat
schedule. Request model `gpt-5.6-luna` with low reasoning effort and confirm the
task, model, effort, schedule, and start signal are product-visible. If that
scheduling surface is unavailable, report `monitoring_unavailable`; do not
create a one-turn observer, substitute a managed subagent or another model, or
make the parent controller poll.

An external observer performs one bounded read-only check per scheduled run. If
it becomes idle before a terminal signal or loses its schedule, job binding, or
required evidence surface, report `monitoring_interrupted` and fail closed. Do
not silently restart it or keep it alive with repeated controller messages.

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
underutilization detection in the same owner or observer contract. Do not create
a second GPU-only observer. Bind the exact GPU devices and job processes,
expected GPU-active phases, explicitly expected low-utilization phases, and at
least one progress signal. Omit this evidence surface only when telemetry is
unavailable, the current phase is explicitly CPU-only, or the user explicitly
excludes it. Use the host-documented read-only telemetry surface. Never infer
persistent underutilization from one snapshot.

Unless job-specific evidence supports another contract, use this balanced GPU
profile:

- observe at `10 -> 10 -> 20 -> 40 -> 60 -> 60 ...` minute intervals, keeping
  the general sparse fallback once the job is clearly healthy;
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

The observer's read-only restriction is a semantic task boundary. It may read
only the named process/session, log, status, and output evidence. It must never
mutate the job or artifacts, send control signals, diagnose by changing state,
execute a contingency, decide success, or advance a phase. Each event reports
the exact evidence identity, observed transition, and uncertainty.

Treat scheduling and observer liveness as part of the contract. If a schedule
does not start, an observer exits unexpectedly, a required surface becomes
unreadable, or a report is missed beyond the declared tolerance, fail closed
with `monitoring_unavailable` or `monitoring_interrupted` and wait for the user.
Do not silently spawn a replacement or make the controller poll.

On a terminal job signal, phase change, authorization withdrawal, or observer
boundary failure, the monitoring owner reports its last evidence, pauses any
schedule, and stops. The main process performs intake only after a native task
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
