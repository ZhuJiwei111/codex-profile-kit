---
name: personal-multiline-coordination
description: Coordinate persistent Codex App tasks, isolated Git worktrees, cross-line intake, and explicitly authorized active-monitoring tasks; use implicitly only for read-only ownership reconciliation when existing tasks or worktrees are ambiguous.
---

# Personal Multiline Coordination

Coordinate durable lines that need their own Codex App task, worktree, or
recurring observation lifecycle. Use `personal-subagent-boundaries` for bounded
one-shot work.

The main process is the control plane. It owns decomposition, authority,
scheduling, cross-line decisions, intake, and the final synthesis. App tasks
perform substantive line work or recurring observation and stop at their
assigned boundary.

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
5. Wait for native task events or bounded controller wakeups. On handoff,
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

Before creation, the main process fixes the exact job identity, evidence
surfaces, progress and terminal signals, observation limits, expected duration,
and cadence. Choose a cadence that matches the job. When there is no better
job-specific basis, use the fallback intervals `20 -> 40 -> 60 -> 60 ...`
minutes. The main process owns this choice and may change it only from fresh
evidence or a new user instruction.

For every GPU-backed long-running job under active monitoring, include GPU
underutilization detection in the same observer contract. Do not create a
second GPU-only observer. Bind the exact GPU devices and job processes,
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

Create one dedicated Codex App task for the observer with model
`gpt-5.6-luna` and low reasoning effort. Confirm that the requested task,
model, effort, and start/liveness signal are product-visible. If the App task
surface cannot request or confirm them, do not start monitoring. Do not fall
back to a custom agent, managed subagent, another model, or recurring polling
by the main process without a new explicit user choice.

The observer's read-only restriction is a semantic task boundary. It may read
only the named process/session, log, status, and output evidence and may wait at
the assigned cadence. It must never mutate the job or artifacts, send control
signals, diagnose by changing state, execute a contingency, decide success, or
advance a phase. Each event reports the observation time, exact evidence
identity, observed transition, and uncertainty to the controller.

Treat observer liveness as part of the contract. If the observer does not
start, exits unexpectedly, loses the exact job/evidence binding, cannot read a
required surface, or misses a required report beyond the declared tolerance,
fail closed: report monitoring as unavailable or interrupted and wait for the
user. Do not silently spawn a replacement or make the controller poll.

On a terminal job signal, phase change, authorization withdrawal, or observer
boundary failure, the observer reports its last evidence and stops. The main
process performs intake and alone decides what the evidence means and whether
any separately authorized action should follow.

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
