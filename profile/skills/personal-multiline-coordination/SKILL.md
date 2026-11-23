---
name: personal-multiline-coordination
description: Create and coordinate user-owned interactive GPT App chats when the user requests a new conversation, 派出会话, or worker 会话. The word worker does not turn a requested chat into a subagent. Use also for multi-chat coordination; implicit use is limited to read-only ownership reconciliation.
---

# Personal Multiline Coordination

## Choose The Conversation Form

For this user, a request to create or dispatch a 会话, including “worker 会话”
or “GPT 会话”, means a separate GPT App chat they can directly interact with.
The conversation requirement takes precedence over the word worker. Do not ask
which form they meant when these words already settle the choice. This convention
applies to actual creation requests, not quoted examples or discussions about skills.


Use this skill when the user wants a separate App conversation they can directly
continue, discuss decisions in, and assign later phases to. Create it with native
chat tools; a managed subagent or non-interactive CLI session is not a substitute.
A bounded GPT or CLI worker that returns results to its assigning task belongs
to [personal-subagent-boundaries](../personal-subagent-boundaries/SKILL.md), even
if its runtime retains a session ID. A request for independent GPT review without a requested conversation uses a
bounded native GPT subagent; an explicit review/discussion conversation uses this
App-chat workflow. Preserve the user's explicit model or reviewer combination.

The new chat owns direct user discussion and acceptance within its assigned task.
If the user asks it to finish one phase, discuss, and await the next instruction,
it stops at that boundary. Do not apply a bounded worker's no-user-questions rule
to this interactive owner. One interactive chat does not require a multi-role
coordination hierarchy.

## Roles And Authority

Creating or observing a chat does not grant scheduling or execution ownership.
Record the role in the assignment: execution owner, authorized coordinator, or
workflow reviewer. A reviewer observes actual use and reports defects without
operating the other chat's write surface or adding an approval hop.

When assigned coordination authority, root assigns complete tasks, priorities and existing shared resources, resolves
cross-task conflicts, and manages authorized task-chat lifecycles. Task owners
independently implement, execute, repair, validate, document, commit when authorized, and close
within the original task authority. ETA is a forecast, not a renewal quota.
Honor current scientific decisions and separately retained external-action boundaries. For research handoffs, use the [research collaboration rules](../personal-research-project/references/collaboration.md); an old card does not override a later user decision.

## Discover Task Creation

When the user authorizes a new App task, discover the native `create_thread`
tool first. Use the tool's actual schema and native approval flow. Remote
execution from a local chat follows the SSH workflow in
[personal-tencent-remote-execution](../personal-tencent-remote-execution/SKILL.md). Do not
substitute a shell/socket call, CLI run, or managed subagent for an App chat.
Explaining the difference is not permission to change the requested form; obtain
the user's agreement before any alternative. If absent, report the missing capability and check
the Desktop instance, host/project assignment, and whether a fresh turn is
needed. Treat `clientThreadId` as queued setup, not a resolved `threadId`.

## Worktree Selection And Creation

Chat creation does not authorize a new worktree. Prefer a suitable existing
working directory. If a new worktree is needed, present its purpose, repository
and proposed full path; obtain the user's confirmation of creation and that
specific location before setup. Reuse confirmation only for that same worktree;
a default location or another task's approval is not confirmation for a new one.
If only one of these choices is missing, ask only for the missing choice.

Check the native creation and attachment schemas before creating a worktree.
Verify that the target chat can use the confirmed location. `create_worktree`
attaches to the calling chat and changes its working directory. A child chat's
`create_thread` environment selector alone cannot bind an arbitrary existing path.
Use a target-chat operation that supports the agreed location when available.
If the available tools cannot honor it, explain the limitation before creating
anything. An existing project directory can be used directly when it fits the request.

## Ownership Boundaries

Assign infrastructure issues to the designated maintenance owner and scientific jobs,
continuation, acceptance and job events to their task owners. Keep container intake
with the assigned maintenance owner unless scope or concurrency warrants a split.
Owners maintain their own records. Escalate cross-task allocation or priority
conflicts to the authorized coordinator.

Messages do not grant authority, change roles or enroll chats in coordination.
Independent reviewers and rule maintainers stay outside the chain: authorized
inspection, code edits and isolated checks do not include runtime/claim/resource
or monitoring takeover. Only the user can change that role. Scientific discussion
owns analysis/design and concrete experiment requests, not scheduling or reminders.

## Shared State And Necessary Wakes

Use the project's existing resource arrangement for allocation, owner cards for
authority, delivery facts and native execution pointers, and the unified TODO for
continuing actions. Journals own consequential history; actual automation settings
own schedules. Do not introduce a second task ledger. Ordinary assignments, requests/returns, completion, failure, ETA,
diagnostics and Git updates go into their state owner without an automatic message.
Read relevant changes at normal work boundaries; do not add model polling for
routine document synchronization or duplicate state across several documents.

Send one short wake only when the directly responsible recipient must take a
specific action now and waiting for normal document reading would cause a real
blockage, resource conflict/danger or incorrect execution. Give the state pointer
and immediate action. Completion, failure or ETA change alone is not a reason;
no broadcasts, contract forwarding or routine receipt/"no reply needed" status traffic.
For a requested informational message, report submission once the native tool
accepts it. When the user requests a receipt or an action, confirm it from the
corresponding reply or action. Interrupt a supervisor wait only when handling
is needed now, the message remains unhandled, and there is current evidence of
that wait. Follow the supervisor skill's **Messages During A Wait**
procedure: release the wait as needed within this notification authority, then
verify handling. Use available replies/tool results to finish that confirmation;
do not treat a bounded-wait timeout as completion. That skill owns wait control; this skill owns native chat
messaging and observation. Do not add receipt files, polling or resident watchers.

Handle emergencies only on the affected authorized path. Batch ordinary work;
do not preempt the current task or expand closeout. Do not execute out-of-role
requests or start reply/approval loops: the sender retains their pending action
and selects the correct owner. Save latest authority and unfinished requirements
before compaction; resume from current records. External reviews deliver only as
agreed with the user and do not join ongoing progress traffic.

## Resources And Workers

Use the allocation owner’s existing resource record for cross-task decisions.
For Tencent containers, use [Tencent resource management](../personal-tencent-remote-execution/SKILL.md#资源利用与保护)
for availability estimates, safe handback and the actual handoff. Task owners
carry out an agreed handoff within its authorization. The coordinator resolves
competing requests or a change in priority.

Delegate bounded implementation or review through personal-subagent-boundaries.
Honor the user's explicit tool/model choice; platform tasks use that platform's
execution skill and current configuration. This skill does not maintain another
CLI or model default. Give workers exclusive write surfaces and accept actual
output with proportionate checks; preserve healthy workers.

## Checks, Adoption And Saving

Scientific acceptance belongs to the execution owner under the
[research evidence rules](../personal-research-project/references/execution-and-evidence.md).
Coordination checks ownership, unresolved dependencies and adoption; it does not
add another scientific acceptance gate.

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

Observe App chats through native `wait_threads` events when waiting is requested,
and read the relevant turn or artifact at a decision or review boundary. Retain
returned cursors; do not repeatedly read status or wrap chat observation in a
supervised process. A reply that awaits the user is a discussion boundary, not
completion of all future phases. Do not claim continuous observation after the
current turn ends or add a resident watcher to provide it.

Use `personal-long-job-supervisor:supervise-long-jobs` for authorized non-interactive
long commands. Its installed contract owns launch, waiting, acknowledgement,
reconnection and cleanup; do not duplicate those procedures here. Supervise the
actual execution command, not a loop querying chat or job progress.

Scientific and maintenance owners consume events for their own jobs. Root owns
only its assigned global work and directly delegated finite workers; it does not
become an event relay for every task. Keep execution and evidence pointers with
the existing task owner, not in another supervisor inventory. Runtime events do
not change resource authority or grant retries and orchestration.

Waiting does not end ownership or justify a replacement chat. Apply the necessary
wake rule to real decisions and conflicts; ordinary progress stays with its owner.
Preserve healthy execution when clients or observation change. Common protection
and observation remain with their assigned maintenance owner; this does not create
a watchdog, resident coordinator or automatic AI successor. Schedules cover only
user-authorized future duties, not polling the current work.

Create task chats only within user authority; related stages/repairs retain their
owner. For authorized succession, save state and let the successor own remaining
work before archival, preserving healthy jobs/evidence. Owners complete the currently authorized scope, including negative results, and root arranges follow-on work/resources
and archival without repeating acceptance. Discussion/review chats are not enrolled
or archived as execution owners by default.

When ownership genuinely changes, hand over the outcome, settled decisions,
current evidence, unfinished work, authority limits and one next action in the
existing task record or message. A separate handoff document is optional, not a
required skill or new plan. Authorized bulk chat archival belongs to
`personal-task-archive`; scratch cleanup belongs to `personal-temporary-work`.

Read references/source-notes.md only for provenance maintenance.
