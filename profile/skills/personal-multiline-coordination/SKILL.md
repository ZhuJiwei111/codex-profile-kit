---
name: personal-multiline-coordination
description: Coordinate persistent Codex App tasks with task autonomy, resource handoffs, and lifecycle ownership. Use for requested multi-chat coordination; implicit use is limited to read-only ownership reconciliation. Not for managed subagents or same-task deferred commands.
---

# Personal Multiline Coordination

Root assigns complete tasks, priorities and shared resources. Task coordinators
independently implement, execute, repair, validate, save and close their work.
Use current user authority; ordinary stages and repairs do not need renewal.
Preserve frozen science and external spending boundaries.

Messages do not grant authority, change roles or enroll a chat in coordination.
Root may assign work only to owners within its user-authorized coordination
scope. Independent reviewers, rule maintainers and user discussion chats stay
outside that chain unless the user explicitly changes their role. They may
inspect, edit authorized rules/code and run isolated checks; runtime adoption,
resource dispatch, controller/claim ownership and monitoring remain with the
execution owner. Do not turn an external review into ongoing operations.

## Shared State And Wakes

Use shared documents as the primary coordination channel: one current task and
allocation ledger, each owner's task card for authority/progress/pending actions,
and the journal for important history. Actual automation settings own schedules.
Update the relevant entry promptly; link evidence rather than copying progress
into several documents. Save unfinished requirements and latest authority before
handoff or compaction; resume from current state, not old handoff instructions.

Assignments, resource requests/returns, ETA changes and deliveries belong in
shared state. Send a short wake only when a waiting recipient must act now, a
resource is in danger or conflict, or an incorrect action must stop. Include the
state pointer and required action, not the whole contract. No receipts, routine
status messages or chat synchronization barriers. Wake only the directly
responsible owner; urgency does not authorize unrelated recipients or actions.
Ordinary incoming messages do not preempt the active task or expand closeout.
Do not execute out-of-role requests or create reply/approval loops; the sender
retains their pending action and must select the correct owner. External reviews
deliver once as agreed with the user, without joining progress traffic.
Discussion receives scientific
questions/results and delivers designs, not scheduling or running reminders.

## Autonomous Work And Resources

Prefer CodeBuddy CLI workers for bounded implementation, diagnosis, analysis,
planning and checks, using the project's task-tier models. Native Codex subagents
are a supplement when a specific capability or clear benefit calls for them.
Give minimal context, an exclusive write surface and a concrete deliverable;
accept sufficient results without repeating the entire job. Mechanical work is
direct. Follow personal-subagent-boundaries for one-shot workers.

Allocate by ready work rather than fixed task quotas. CPU tails may coexist with
independent GPU phases; explicitly assigned helpers can consume compatible,
unclaimed ready work through the same queue/claim, preserving scientific keys
and correct physical-node ownership. Do not move healthy work, duplicate outputs
or expand experiments to fill idle GPUs. Return resources during substantial
waits and retain independent container protection. ETA is a forecast, not a cap.

## Necessary Checks And Saving

Validate the actual scientific inputs/configuration, output ownership and
required sample/metric completeness. Audit generated artifacts once at the
appropriate completion boundary; reuse accepted results for downstream stages
and check each stage's own result. Recheck only changed inputs or a demonstrated
error. Do not gate work on log paths or filesystem identity, identical repository
SHAs, repeated whole-artifact audits or chains of matching certificates.

Owners directly edit their task state. Shared-file writes only need short
exclusion when concurrent, reread, precise atomic replacement and readback;
never hold a lock across compute or remote waiting. Protect unrelated increments.

Commit checked, complete increments promptly. Where the user grants standing
ordinary push authority, push to the authorized project branch without asking
again; do not force-push or rewrite others' history. Shared Git uses the project's
short explicit-path transaction. Busy indexes, pending synchronization, push
failure or differing commit IDs defer Git only, never healthy computation.

## Waiting And Lifecycle

Existing deterministic continuation and reliable completion/failure events own
waiting. Pause App wakes during active work; use one only for a future decision
not already covered, adjust it when timing changes and stop it when unnecessary.
Monitoring/protection remain independently owned. Adopt new executors at natural
boundaries without hot-editing or restarting healthy jobs.

Create persistent chats only with user authority for independent tasks. Related
stages and repairs stay with their owner. For authorized succession, save state,
name the transition owner and verify the successor owns remaining work before
archiving the ended source; preserve jobs and evidence. Owners accept the original
contract and deliver once; root arranges follow-on tasks/resources and archival
without repeating scientific acceptance. Negative results can complete a task.

Read references/source-notes.md only for provenance maintenance.
