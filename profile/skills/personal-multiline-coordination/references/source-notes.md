# Source Notes

Updated: 2026-10-22.

This is a local workflow derived from user-directed coordination of persistent
Codex App chats and Git worktrees. Earlier experience established exact
task/cwd/worktree identity, exclusive write surfaces, one integration owner,
and evidence-bearing handoffs.

The October 20 multi-turn project restructuring exposed repeated root/task
messages, unnecessary reauthorization, an overloaded root, shared-index
negotiation, and schedules left active or stale after task changes. The user
requested complete-task chats, autonomous task-local execution within assigned
resources, resource returns before final completion when appropriate, and
verified lifecycle closure including automations and archival.

The user also distinguished scientific discussion from scheduling: root may
request result analysis, experiment design, and analysis design; discussion may
send a restrained, concrete experiment-scheduling request back to root.
Scientific evidence and constraints travel with the request, not operational
timetables or routine resource traffic.

The same user subsequently delegated existing-project GPU scheduling directly
to root and authorized both root and task coordinators to use subagents.
Compute should be allocated generously according to useful task work, with
estimated duration rather than artificial minute caps or repeated diagnostic
quota approvals. This supersedes micro-allocation gates for those authorized
tasks; actual resource expiry, scientific criteria, and separately retained
spending limits remain distinct.

A follow-up audit found task-internal diagnostic milestones still sent to root
with "no reply needed" despite autonomous continuation. The workflow now makes
the recipient-action/resource/commitment boundary explicit and keeps related
probes under one continuing allocation, with internal ETA changes saved to the
task rather than driving extra root wakeups.

The user then authorized coordinators to commit their own checked stage work
promptly and requested waiting-phase App scheduling: pause reminders while
actively working, finish the current basics, and arm a useful future check only
when waiting. Container CLI monitoring and handling continue independently.
Shared-index serialization remains distinct from asking for commit permission.

A further read-only audit found a long root turn with repeated incoming work
and a context-compaction marker. The wording briefly returned to an older
limited approval after broader authority had already been accepted; later
execution did use the new authority. This does not prove that compaction lost
requests. The user requested urgent intake, durable ordinary-work registration,
bounded closeout batches, and preservation of unfinished requirements and
latest authority before compaction. Related changes are completed and checked
before one delivery to root.

A later resource-request audit found that multi-document preparation delayed
dispatch despite a short live resource check. The user requested one allocation
ledger and immediate dispatch after necessary checks, with logs, replicas, and
commits deferred to later batches. Existing container agent CLIs may be useful
bounded workers when delegation has a net benefit, not another scheduling hop.

The user then authorized coordinators to edit their own TODO/journal entries
directly, rather than message root for routine document updates. Existing
anchored atomic-write tooling and historical use were verified. The installed
helper described a lock in prose but did not implement that CLI option, so the
project uses a shared short mkdir lock around the operation. Document editing
and shared Git-index serialization remain separate responsibilities.

The user requested a full consolidation: root only assigns tasks/resources and
resolves cross-task conflicts, while task owners execute, document, validate,
commit, and close independently. Routine adoption/launch/commit reports and
root reacceptance are removed; locking is limited to real concurrent writes
and must not stall independent work. The entrypoint was rewritten around
these boundaries rather than retaining accumulated incident checklists.

These lessons inform the workflow, not blanket permissions. User authorization
must cover actual chat actions and execution. Specific task IDs, GPU counts,
host paths, budgets, and monitoring mechanisms remain project state. Managed
subagents and external-job supervision retain their separate workflows.

The October 21 consolidation makes ordinary events document-only and permits a
short wake only for a direct owner's immediate actionable dependency or danger.
Completion, failure, ETA changes and no-reply wording do not independently
justify messages. Project configuration/maintenance have execution owners; root
is not a default editor/operator, and external reviewers never become runtime
owners through messages. Rule publication and actual runtime adoption remain
distinct. Node idle ETA includes that node's queued GPU work and is separate
from overall task completion and container expiry.

An approved October 21 follow-up separates common maintenance from scientific
job ownership and resource scheduling. Supervisor waiting is not abandonment;
native waits are not supervised jobs. Common checks filter ordinary advisories,
and intake does not automatically create a permanent owner per container.

The October 22 user-approved follow-up uses TCodex/GPT-6.1-sol for ordinary
implementation and CPU checks, TClaude/Opus-5.5 for complex diagnosis/design,
and CodeBuddy/DeepSeek Flash for simple tasks. Real CPU deliveries and owner
acceptance support entrypoint use, not a controlled CLI ranking. Exact routed
arguments belong to project operations. Apply to new work without duplicate
dispatch, a new coordination layer or interruption of healthy workers.
