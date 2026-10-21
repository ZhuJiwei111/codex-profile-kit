---
name: personal-multiline-coordination
description: Coordinate persistent Codex App tasks with task autonomy, resource handoffs, and lifecycle ownership. Use for requested multi-chat coordination; implicit use is limited to read-only ownership reconciliation. Not for managed subagents or same-task deferred commands.
---

# Personal Multiline Coordination

## Roles And Authority

Root assigns complete tasks, priorities and existing shared resources, resolves
cross-task conflicts, and manages authorized task-chat lifecycles. Task owners
independently implement, execute, repair, validate, document, commit and close
within the original task authority. ETA is a forecast, not a renewal quota.
Preserve frozen science and separately retained external-action boundaries.

Public maintenance owns shared environments/tools, container intake and the
availability of common protection/monitoring, including actual infrastructure
failures. Scientific owners retain their jobs, continuation, acceptance and job
events; root retains scheduling. Prefer one maintenance owner across existing
containers. Intake is a bounded deliverable, not automatically another permanent
chat. Split only for real independent scope, write surfaces or concurrency, with
ongoing ownership explicit. Maintenance is not a scientific approval hop.
Shared-code integration and configuration likewise have concrete execution owners;
root assigns rather than operates. Owners edit task-related shared records directly.


Common checks cover guard/watchdog health, registered-node coverage, required
idle protection without contention with real work, sustained utilization in task
context, and actionable maintenance inbox events. Use existing records/thresholds;
do not duplicate GPU sampling. Expected preparation/CPU tails, ordinary inbox
updates and unchanged advisories stay in background records. Infrastructure
failures belong to maintenance; task progress/scientific checks belong to task
owners. Escalate actionable allocation/priority decisions to root, never reassign
GPUs or start experiments merely because utilization is low.

Messages do not grant authority, change roles or enroll chats in coordination.
Independent reviewers and rule maintainers stay outside the chain: authorized
inspection, code edits and isolated checks do not include runtime/claim/resource
or monitoring takeover. Only the user can change that role. Scientific discussion
owns analysis/design and concrete experiment requests, not scheduling or reminders.

## Shared State And Necessary Wakes

Use one task/allocation ledger, owner task cards for authority, actual execution
and unfinished work, journals for important history, and actual automation settings
for schedules. Ordinary assignments, requests/returns, completion, failure, ETA,
diagnostics and Git updates go into their state owner without an automatic message.
Read relevant changes at normal work boundaries; do not add model polling for
routine document synchronization or duplicate state across several documents.

Send one short wake only when the directly responsible recipient must take a
specific action now and waiting for normal document reading would cause a real
blockage, resource conflict/danger or incorrect execution. Give the state pointer
and immediate action. Completion, failure or ETA change alone is not a reason;
no broadcasts, contract forwarding, receipts or "no reply needed" status traffic.
Resource dispatch needs necessary authority/ownership/live checks and one ledger
update; logs, replicas and Git follow without delaying authorized execution.

Handle emergencies only on the affected authorized path. Batch ordinary work;
do not preempt the current task or expand closeout. Do not execute out-of-role
requests or start reply/approval loops: the sender retains their pending action
and selects the correct owner. Save latest authority and unfinished requirements
before compaction; resume from current records. External reviews deliver only as
agreed with the user and do not join ongoing progress traffic.

## Resources And Workers

Allocate generously by ready work. Return GPUs during substantial CPU tails or
waits; compatible helpers consume the same atomic queue/claim and scientific keys
under correct physical resource ownership. Do not move healthy work, duplicate
outputs or expand experiments to fill idle GPUs. Retain independent protection.

Group the resource table by task/actual work, with one row for all nodes serving
that task. Use the project's fixed columns: task/current progress, nodes/GPU count,
next stage (estimated), current-task handback, forecast node availability, and
queued successors. Keep explicit node/GPU ranges and totals; shared-node tasks
must not double-count GPUs. If availability differs, list node groups and times
within the same task row.

Forecast availability after current and already queued GPU work, distinct from
task handback, next stage, overall completion and container expiry. Prefer concrete
local dates/times marked estimated. Use current measured progress/throughput and
queued successors; when successor throughput is unavailable, give a provisional
estimate from measured comparable work and explicit assumptions. State the brief
basis, observation time and uncertainty; unaccepted technical speeds are not
formal training evidence. Scheduling assumptions do not alter scientific stop or
selection rules. Correct estimates as progress, successors or material deviations
change. Do not leave "pending calibration" indefinitely: if no estimate is defensible,
name the missing evidence and next update milestone. Keep the overall estimate
concise and shown once, with expiry separate; add no second ledger, polling,
approvals or reporting workflow.

Default ordinary code implementation, changes and CPU checks to bounded TCodex
workers with GPT-6.1-sol. Use TClaude with Opus-5.5 for complex diagnosis, design
and planning; retain CodeBuddy with DeepSeek Flash for simple bounded tasks.
Use the project operations guide for verified native arguments, installed paths
and exact routed model IDs; do not transfer aliases between CLIs. Give minimal
context and exclusive write surfaces. Native subagents supplement a specific
capability or clear benefit; mechanical work stays direct. The task owner decides
and accepts actual output with proportionate checks, without duplicate dispatch
to compare tools, mandatory second review or a new coordination layer. Apply this
choice to new work; preserve healthy workers. Use personal-subagent-boundaries
for workers.

## Checks, Adoption And Saving

Check actual scientific inputs/configuration, unique writers and required sample/
metric completeness. Audit generated artifacts once and reuse accepted results;
check each stage's own output. Recheck changed inputs or demonstrated errors only.
Do not gate on log paths/filesystem identity, matching repository SHAs, repeated
whole-artifact audits or chains of certificates.

A rule/source change does not establish runtime adoption. Execution owners record
the actual entrypoint and adopted/pending scope in their existing task card and
switch at natural boundaries. Do not hot-edit healthy jobs, require every old job
to upgrade at once, repeat scientific acceptance or turn the reviewer into operator.

Shared writes need reread, precise atomic replacement and short exclusion only
for real concurrency; never hold locks across compute or remote waits. Where the
user grants standing commit/ordinary push authority, save checked increments
promptly on the authorized project branch. No force-push or rewriting others'
history. A busy index, failed push or different commit IDs defers Git only; do not
broadcast a pause on all document editing or require globally clean worktrees.

## Waiting And Lifecycle

For authorized long commands, use `personal-long-job-supervisor:supervise-long-jobs`
for launch/observation, `wait_event(job_id)` for one job or native `wait_any(job_ids)`
for several, diagnosis, acknowledgement and registration cleanup. Returned events
keep their original job/event IDs and are not automatically acknowledged. Root
waits only for its own global decisions; scientific and maintenance owners consume
their own events rather than routing everything through root. Read that skill when using the supervisor; do not copy its
monitor defaults or infer orchestration/retry/resource authority from an event.
Execution and sampling stay detached; existing executors own authorized continuation.

Common guards sample/protect. An observation bridge, when needed, reads existing
records and emits conditions requiring owner action. Healthy heartbeats, arbitrary
inbox growth or expected preparation/holder-only status do not automatically wake
the model. Keep the actual job/event pointers, actionable conditions and owner in
the existing task card, not duplicated supervisor inventories.

Use native `wait_any` when several independent jobs need observation. Retain an
existing genuine observer that reads several containers' records for one maintenance
duty; do not split it just to adopt the API. Never supervise wait calls or wrappers
polling supervisor status, add resident coordinators, or restart healthy observation
and compute merely to upgrade the waiting client.

Waiting is not abandonment, loss of ownership or grounds for a replacement chat.
Ordinary new work waits for the owner's next boundary; immediate work follows the
necessary-wake rule. Root or the responsible owner may use `interrupt_wait(job_id)`
when a wait really must be released: it requests interruption of existing waits
watching that job, including multi-job waits across MCP instances sharing state.
It does not stop workers/targets, acknowledge events, confirm a waiter exists or
affect later waits. Do not use it to chase ordinary progress; external reviewers
do not take over waits. Older waiting code does not observe the new control;
reload clients at idle boundaries without restarting background jobs.

After handling current authority and pending work, rejoin only viable observation.
If `waitable=false` and no event remains pending, stop waiting; supervisor loss
alone does not establish target failure. Chat messages are not guaranteed to
interrupt the host. On `Transport closed`, retain job IDs and follow the supervisor's
inspection/recovery guidance; do not automatically recreate chats or relaunch jobs.

Pause App wakes during active work; schedule only uncovered future decisions,
adjust changed ETAs and stop obsolete wakes. Background protection persists across
chat waits/pauses. Retire finite registrations per the supervisor skill; retain
useful resident observation until the duty ends or an explicit successor owns it.
Do not notify chats merely because an event arrived.

Create task chats only within user authority; related stages/repairs retain their
owner. For authorized succession, save state and let the successor own remaining
work before archival, preserving healthy jobs/evidence. Owners accept the original
contract, including negative results, and root arranges follow-on work/resources
and archival without repeating acceptance. Discussion/review chats are not enrolled
or archived as execution owners by default.

Read references/source-notes.md only for provenance maintenance.
