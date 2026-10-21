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

A node's forecast idle time means completion of its current and already queued
GPU work, when it becomes available for new scheduling. Keep that distinct from
the current task's handback, next stage, overall task completion and container
expiry. Prefer a concrete local date/time estimate for node availability, based
on remaining work, measured throughput and queued successors. Mark it estimated;
if not estimable, state the calibration gap rather than inventing precision or
copying an overall window. Use the project's single concise resource table.

Prefer bounded CodeBuddy CLI workers using project model tiers and exclusive
write surfaces. Native subagents supplement a specific capability or clear benefit.
Mechanical work stays direct. The owner decides and accepts sufficient results
without mandatory duplicate review; use personal-subagent-boundaries for workers.

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
for launch/observation, native `wait_event(job_id)`, diagnosis, acknowledgement and
registration cleanup. Read that skill when using the supervisor; do not copy its
monitor defaults or infer orchestration/retry/resource authority from an event.
Execution and sampling stay detached; existing executors own authorized continuation.

Common guards sample/protect. An observation bridge, when needed, reads existing
records and emits conditions requiring owner action. Healthy heartbeats, arbitrary
inbox growth or expected preparation/holder-only status do not automatically wake
the model. Keep the actual job/event pointers, actionable conditions and owner in
the existing task card, not duplicated supervisor inventories.

Use only native waiting/event fan-in actually supported by the interface. A genuine
observer may inspect several containers' existing records for one maintenance duty
and emit one actionable result; it must not just await other supervisor jobs.
Never supervise wait calls, multi-event waiters or wrappers polling supervisor
status. Report missing capability rather than layering supervision or adding
resident coordinators;
retain healthy jobs/observation during natural-boundary adoption.

Waiting is not abandonment, loss of ownership or evidence for a replacement chat.
Save ordinary new work for the owner's next work boundary; use the necessary-wake
rule for immediate work. Steering/cancelling a wait leaves its underlying job
unchanged: reread current authority and pending work, then rejoin useful waits.
Do not assume chat messages can interrupt the host. If they cannot, root may
explicitly give independent urgent work to an available existing owner; waiting
or silence alone never justifies duplicate assignment or a new permanent chat.
Actual transport failure follows the supervisor recovery rules and existing
chat-creation authority.

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
