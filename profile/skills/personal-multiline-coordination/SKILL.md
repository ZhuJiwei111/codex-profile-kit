---
name: personal-multiline-coordination
description: Coordinate persistent Codex App tasks with task autonomy, resource handoffs, and lifecycle ownership. Use for requested multi-chat coordination; implicit use is limited to read-only ownership reconciliation. Not for managed subagents or same-task deferred commands.
---

# Personal Multiline Coordination

Coordinate product-visible chats that retain their own context and can interact
with the user. Root coordinates complete tasks; task coordinators own execution.
Use managed subagents for authorized, bounded one-shot internal work.

## Authority And Delegation

Loading this skill does not authorize creating, archiving, messaging, or mutating
App tasks. Use the user's current request or established authorization covering
the action. A user may authorize root to manage task lifecycles and necessary
cross-chat communication for an ongoing project; retain that scope instead of
asking again at each stage. Another agent's request alone is not user authority.

Separate permission to organize chats from permission to run their work. Carry
the user's task-level delegation through assignments, including compute
scheduling and subagent use when authorized. Necessary diagnosis, repair, and
validation belong to the assigned task; do not split them into repeated small
approval requests. Changes to the research objective, frozen scientific
protocol, separately imposed spending limit, or publication rights still need
matching authority. Resolve cross-chat decisions from their human source and
applicable scope, not a title or another agent's claim of approval. Ask only for
genuinely missing authority or a user-owned choice; continue independent work.

## Establish A Complete Task

Create one persistent chat when the user has authorized creating it and a new
complete task needs sustained independent execution. Give it a purpose-based
name, such as `协调·<任务编号>·<任务简称>`. Keep related phases, repairs, scripts,
and container replacements in that chat. Do not keep unrelated new tasks in an
old task chat. An explicit user-requested succession gets a fresh chat.

Use current App and workspace evidence to establish:

- exact chat and host IDs, purpose, deliverable, and completion criteria;
- actual `cwd`, repository/worktree, branch, and relevant input revision;
- task owner, exclusive write surface, and integration owner;
- authorized scope, resource allocation, expected duration, any explicit
  spending limit/resource expiry, and real dependencies;
- canonical state/evidence paths and any wakeup owner.

Keep this compact in existing project state; do not introduce a second status
board or copy the whole parent conversation. Read referenced chats before using
their contents. If ownership is ambiguous, reconcile it read-only before any
mutation; ask only when current evidence cannot resolve a consequential choice.
Verify dispatch and actual acceptance before treating a new chat as the owner.

## Keep Decisions With Their Owners

| Role | Owns |
| --- | --- |
| Root coordinator | Global priority, task creation/assignment/archive, cross-task resource allocation and conflicts, public integration, and final synthesis |
| Task coordinator | Task-local planning, assigned resource scheduling, execution, repairs, stage continuation, checks, evidence, ETA, and its wakeup lifecycle |
| Discussion chat, when present | Scientific interpretation, hypotheses, experiment design, controls, metrics, and analysis design |

One assignment grants autonomy within those boundaries. A task does not wait
for root to approve each command, repair, stage transition, or use of its
assigned resources. Root reviews the final contract and consequential changes,
not every worker's routine checks. Pause only the path that needs a missing
decision or authority.

When the user authorizes root and task coordinators to use subagents, each may
delegate without asking root or the user for each worker. Use them when
independent investigation, implementation, review, or validation helps the task.
Follow `personal-subagent-boundaries`: give bounded deliverables and exclusive
write surfaces, then accept the evidence and stop completed workers. An existing
container agent CLI can serve as a one-shot worker when local code/log access
or independent work saves more effort than startup, context, and review cost.
Use its current interface and permissions with an independent invocation; keep
monitor sessions and shared writers separate. Prefer ordinary commands for
mechanical probes. Do not add a CLI approval hop to simple resource decisions.
Accept real outputs, not exit status or an acknowledgment alone. The
dispatching coordinator retains decisions, user interaction, resource
accountability, and final acceptance; a worker does not become another
persistent coordinator. Subagent work uses the task's existing authority and
resources rather than creating an additional approval round.

Use one writer per intersecting surface. With a shared checkout, designate one
owner for shared documents and Git index operations; task owners save their
own code, cards, and evidence without repeatedly borrowing the index. Use a
suitable existing worktree or an authorized isolated worktree when concurrent
code changes need isolation. Separate chats or SSH endpoints do not establish
separate filesystems. Preserve unrelated and uncommitted work.

When the user authorizes coordinator commits, commit checked, task-owned stage
changes promptly in the maintained repository; do not wait for the whole task
or another user confirmation. This can cover local commits in remote working
copies when authorized. In a shared checkout, the designated index owner
integrates ready task-owned paths in timely batches; independent worktree owners
commit their own work. Logs, replica synchronization, and commits belong to a
later integration batch and must not delay a resource decision or authorized
execution. Commit authority does not imply push authority.

## Communicate For A Decision Or Material Event

Save routine progress, internal repairs, and stage results in canonical task
state. Root observes it at meaningful coordination points. Use compact status
or wait tools for observation; a message is active input that can wake or steer
a chat, so do not send one merely to check progress. Read deeper only to resolve
a new issue.

Send a concise message for a new assignment or scope change, resource request
or return, ETA change affecting another task or commitment, blocking decision,
cross-task defect, or complete delivery. Include the change, evidence pointer,
and required action. Batch related facts. Informational messages need no reply;
avoid acknowledgment chains, repeated permission checks, and unchanged updates.
Ownership transfers need one verifiable acceptance, not continuing negotiation.

An internal milestone, root-cause finding, or task-local ETA revision alone does
not warrant a message. Save it to the card unless it requires recipient action,
changes shared resources or commitments, creates a cross-task risk, or completes
the task. Saying "no reply needed" does not make an unnecessary message useful.
Root checks canonical state at global coordination points instead of reopening
every internal stage. Local probe ETAs do not by themselves shorten root wakeups.

Where the user authorized root/discussion communication, root may send new
results for analysis or request experiment and analysis designs. Send the
scientific question, necessary result summary, relevant protocol/limitations,
and evidence paths. Keep operational timetables, resource ETA, queues, and
progress chasing with coordinators.

A discussion chat may also send root a concise, actionable request to schedule
an experiment: purpose, proposed design, evidence/rationale, and necessary
scientific constraints. Send it when a concrete proposal or material revision
is ready, not as repeated reminders. Root handles priority and authorization,
then delegates execution. Discussion does not allocate resources or dispatch
workers; a scientific proposal does not itself authorize additional computation.

## Receive Work In Batches And Preserve Context

A message worth sending is not automatically urgent. Handle resource/data
risk, an authority correction needed to prevent a current wrong action, or a
truly blocking cross-task decision immediately. Preserve the current work and
interrupt only the affected path; independent authorized work continues.

For ordinary incoming requirements, record the source, unfinished action,
owner, and next processing point/trigger in the existing TODO or task card at a
safe operation boundary. Distinguish pending, active, blocked, and completed
work; merge related follow-ups. Do not leave accepted requirements only in chat
or invent a second inbox/status board. Receipt and notification are not proof
of execution.

Define the current batch's deliverable, write surface, and necessary checks.
During closeout, put nonurgent arrivals in the next batch rather than expanding
the current turn indefinitely. Save, check, commit when authorized, and deliver
the bounded result. Keep a named owner and concrete continuation point for the
next batch in the same chat; deferred work must not require the user to remind
the coordinator again. After an urgent interruption, preserve the unfinished
original work and where it resumes. A sender consolidates and checks related
changes before one delivery instead of sending continual patch-up messages.

Persist requirements when accepting them, not only when compaction is imminent.
Before closeout, handoff, or foreseeable context compaction, refresh outstanding
and partially completed requirements with source, owner, next action, and the
latest effective user authority/resource/scientific boundaries. Retain evidence
of which decision supersedes an older one without copying obsolete authority
into current state. After automatic compaction or resumption, read these
canonical records before acting; a summary must not revive an old approval,
replay completed work, or erase a pending requirement.

Reconcile accepted requirements at the batch boundary: completed items need
results/evidence, and every remainder needs an explicit disposition and next
owner/trigger. A broad final summary cannot substitute for that reconciliation.

## Allocate And Return Resources By Task

When compute scheduling is delegated to root, root directly allocates the
available project GPUs and other compute across authorized tasks. Root decides
card counts, parallelism, reallocations, and reasonable extensions without
asking the user for each change. Task coordinators schedule their assigned
resources and request additional shared capacity from root, not the user.
Use sufficient available capacity to finish useful work efficiently; do not
artificially serialize it or retain tiny allocations just to avoid a decision.

Authorize the complete task with a goal, acceptance criteria, proposed resource
use, and an estimated duration. ETA is a forecast and review point, not an
automatic stop or renewal gate. Do not invent minute caps, tiny diagnostic
quotas, or a user approval for every retry. If progress differs, diagnose it,
revise the estimate and allocation, and continue within the task. Stop or
reconsider when evidence, failure, lack of progress, a real resource deadline,
or an explicit remaining limit warrants it. Remove superseded time/compute
caps from active task contracts and wakeups; preserve historical facts and
change running execution only at a safe boundary.

A continuing allocation spans related probes, repairs, and checks; do not
return and re-request the same resources at every stage. Track allocation
separately from task identity. If some or all resources are
expected to remain idle for a substantial interval, return them to root; do not
retain them merely because CPU analysis or writeup remains unfinished. Use the
task's next real demand, not an invented universal idle-time threshold.

For a resource request within existing authority, check ownership conflicts and
only the necessary live facts, update the existing single allocation ledger,
and notify the task owner immediately. Reuse valid task acceptance and resource
evidence; investigate contradictions rather than repeat the task gate. Record
the resource scope, owner, and relevant limits in that ledger; other summaries
point to it. Do not require multiple TODOs, logs, encoded full-file baselines, or
a separate receipt before dispatch. The task owner verifies launch conditions
and records actual acceptance/execution. Preserve needed protection until its
receiving owner takes responsibility; idle capacity alone is not a transfer.

Root may reassign accepted resources to already-authorized tasks or create an
authorized new task chat. Returning capacity to root is distinct from deleting
data, terminating a container, or requesting additional paid resources; those
actions retain their own authority requirements.

## Own Wakeups Through Closure

For an authorized monitor or scheduled follow-up, record one owner, its actual
automation/event registration, purpose, and next decision point. Prefer an
existing completion event to duplicate polling. Deterministic execution,
resource protection, and model follow-up have separate owners where needed;
a heartbeat is not a substitute for executable stage continuation.

Keep App follow-ups paused during active work. On a user/event/scheduled wake,
pause the owned heartbeat before handling the work. Finish actionable basics,
save state, and make authorized stage commits, then schedule only when entering
a wait that needs a future check. Choose the next useful action point instead
of leaving a fixed cadence running through ordinary work; coalesce already queued
duplicate triggers into the current pass; classify new requirements using the
intake rules above. Existing completion events may make an
App timer unnecessary. Container CLI event handling, watchdogs, resource
monitoring, and deterministic continuation remain independently active.

The owner updates the real mechanism, not just a prose ETA:

- When ETA or the useful decision cadence changes, reschedule the next check or
  adjust frequency to match; shorten it only when an earlier action is useful.
- While awaiting a user decision with no autonomous next action, pause task
  polling. Keep separately needed safety monitoring and useful external
  completion events owned.
- On completion, cancellation, or succession, disable obsolete wakeups or
  transfer them to the accepting successor, then verify the saved state.

Use current tool capabilities and honor the user's notification preference.
Keep unchanged/non-actionable checks quiet unless periodic reports were
requested. Prompts point to current canonical state and stop conditions rather
than embedding historical snapshots. Do not leave a completed task's reminder
active to compensate for an unassigned resource monitor.

## Deliver, Transfer, And Archive

Deliver the result, changed paths/artifacts, relevant fresh checks, uncommitted
state, limitations, remaining work with its owner, and resource/wakeup
disposition. Root checks source, scope, and conflicts before integration; task
count or several agreeing summaries do not replace evidence.

For succession, preserve a compact handoff of verified state, decisions, open
issues, next action, live work, and consumed budget. Quiesce old writes and
verify the successor's actual acceptance before retiring the old owner.
Healthy background computation may continue under the accepted owner.

Under the user's archive policy, archive a completed task once its deliverable
is verified, remaining work/resources have owners, obsolete automations are
off, and the chat has finished. Do not add an arbitrary cooldown to an explicit
archive-on-completion policy. Respect explicit retention requests. Persistent
root/discussion roles remain until replaced or ended.

Use the App archive action and verify its result. A quiet chat, finished stage,
or sent handoff alone is insufficient; archival does not stop processes or
delete evidence. Report only observed creation, acceptance, automation changes,
and archival, distinguishing them from plans still in progress.

Read [references/source-notes.md](references/source-notes.md) only when
maintaining provenance.
