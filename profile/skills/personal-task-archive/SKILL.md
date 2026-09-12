---
name: personal-task-archive
description: Review and archive Codex tasks on a selected local or remote host, explain retain/archive decisions in conversation, and distinguish task organization from active execution.
---

# Personal Task Archive

Review one host at a time. Archive clear cases when authorized; explain uncertain
cases directly in the conversation so the user can decide.

## Scope And Authority

- Resolve the selected host to an exact product `hostId`; default to the calling
  task's host only when none is specified. Freeze it for this run.
- The local App can manage remote tasks. Pass the frozen host identity to every
  scoped query, runtime snapshot, message, archive, and verification. If a tool
  cannot address that host, report the capability gap rather than using its default.
- Use target-host paths, shell, and `CODEX_HOME` for filesystem inventory. Read
  [session-inventory.md](references/session-inventory.md) when acquiring metadata
  or supplementing missing product signals; its bounded global lookup is the
  only task-query exception.
- An archival request authorizes eligible archives. Audit or recommendation
  requests authorize inspection only. Skill editing does not authorize archival.
- Use product archive actions; history stays intact. Keep inspection to bounded
  metadata and task summaries, excluding raw transcripts, rollout JSONL, SQLite,
  auth/session payloads, attachments, caches, and logs.
- Archival does not stop execution or traffic. If the request concerns ongoing
  activity, diagnose the command, Goal, automation, or runtime before returning
  to task organization. Do not cancel or restart anything through this skill.
- Memory work is separate and opt-in. Only when explicitly requested, read
  [memory-hygiene.md](references/memory-hygiene.md); that branch remains scoped
  to the calling task's execution host.

## Decision Rules

Protect the calling task, explicitly identified main task, running tasks, known
Goals, automations, unread or pinned tasks, and tasks the user unarchives during
this run. Pinning provides durable protection; do not maintain hidden exclusions.
Known material unfinished work or unresolved user decisions also require retention
unless an explicit successor already owns all remaining work.

Measure age from the last substantive request or result. Maintenance events do
not reset it. If only a generic update time exists, use it conservatively.

| Evidence after protection checks | Decision when archival is authorized |
| --- | --- |
| Completed independent task, less than 24 hours old | Retain temporarily without asking. |
| Completed independent task, 24 hours to 15 days old, clearly lightweight | Archive. |
| Completed independent task, 24 hours to 15 days old, not clearly lightweight | Present for user review. |
| Completed independent task, more than 15 days old | Archive. |
| Explicit successor owns all remaining work | Archive after any necessary handoff. |
| Product-confirmed subAgent, finished and delivered, or parent explicitly owns remaining work | Archive regardless of age. |
| Product-confirmed subAgent without an identifiable parent, more than 6 days old | Apply the parentless route below. |
| Parentless subAgent at most 6 days old | Retain unless completion and delivery are independently established. |
| Failed with a material next action | Retain; failure alone is not completion. |
| Failure explicitly abandoned, terminated, or moved to a confirmed successor | Archive. |

Lightweight means one verified routine outcome, no material next action, and
little continuing design, diagnostic, implementation, or reference value.
Optional suggestions after completion do not themselves make work unfinished.

Succession requires an explicit link from the user, source, or successor and
actual ownership of the remaining work. Similar titles, shared repositories,
newer tasks, and copying a summary are insufficient.

Identify subAgents from product source or parent metadata, never titles. A
parent ID is not proof of delivery; an unarchived parent is not a reason to
retain a finished, delivered child. Read only the bounded parent evidence
needed to resolve delivery or ownership.

### Parentless SubAgents

A parentless subAgent older than 6 days may be archived if the product runtime
confirms it is not running and no known protection or material pending work
applies. Missing parent or delivery evidence alone does not block this route.
Unavailable pin, unread, Goal, or automation fields are disclosed once and may
remain unknown under this route; known protection always wins. Unknown runtime
status still blocks archival. Age alone never proves inactivity.

### Evidence Gaps And Exact Confirmation

Record signals as present, absent, or unknown. Ordinary automatic selection
requires resolved protection signals; the parentless route is the exception.
A separate app-server's `notLoaded` does not prove that another instance is idle.
Use a product runtime snapshot when the exact read does not establish activity.

For exact targets the user confirms after disclosure of missing pin, unread,
Goal, or automation fields, proceed after checking current outcome and runtime.
Do not ask again about the same disclosed gap. This does not override known
protection, uncertain host/target identity, running or unknown execution,
material pending work, or unresolved ownership outside the parentless route.

Exhaust bounded complementary lookups once. Revisit only when tools or relevant
state change; report unresolved evidence rather than restarting discovery.

## Review A Host

1. For a fresh cleanup, acquire the complete target-host metadata inventory
   described in the reference, including child sources and exhausted pagination.
   Record raw unarchived main-task and subAgent totals before exclusions. A capped,
   cross-host, or child-omitting list cannot establish those totals.
2. Apply metadata-known protections before deep reads. Recent independent tasks
   can be excluded immediately; recent children may still qualify through
   completion and delivery. Parentless children older than 6 days remain candidates.
3. Sort candidates oldest first. Read at most 50 distinct tasks in a normal run,
   including any parent/successor reads. Inspect latest outcome, required next
   action, ownership, and protection evidence; avoid loading an entire conversation.
4. Record `No Codex thread found` once as missing/stale/unsupported; never retry
   it as a mutation. Empty turns mean missing outcome evidence, not completion.
5. Present decisions using the format below. For an already-confirmed exact list,
   reuse prior inventory and go directly to fresh target checks instead of repeating
   the host-wide review.

## Explain In Conversation

Default to an inline review, not a report document. Create a separate document
only when explicitly requested. Scratch metadata is not a user-facing deliverable.

Lead with host, raw totals, and the actionable result. Then explain:

- **Archive / recommend archive:** link each task with one specific reason;
  distinguish authorized automatic actions from cases needing a decision.
- **Retain:** link independent tasks with their concrete pending work or protection.
  Group repetitive guardian records by source, count, age range, and shared reason;
  expose individual IDs only when needed for a decision or requested by the user.
- **Needs a decision:** use `[@Exact product title](thread://ID)` and a one-sentence
  state/recommendation. Use the ID if untitled. Link both source and successor
  when succession is the reason. Batch related choices into one concise question.

Keep raw totals, excluded, read, eligible, and deferred counts distinct. Mention
missing records, material tool limits, and candidates beyond the 50-task cap.
Avoid forcing empty categories or hiding the analysis behind a file link.

## Execute And Verify

1. Immediately before each archive, exact-read the target on the frozen host.
   Obtain a runtime snapshot if necessary. Changed protection, outcome, or ownership
   moves it back to retention/review; unchanged approved gaps need no reconfirmation.
2. Send no summary by default: archival preserves history. A minimal handoff is
   appropriate only when an explicit successor lacks necessary information and
   sending that message is authorized; verify delivery before archival.
3. Archive exact IDs through the product action. Verify each actual target on
   the same host. If the product archive list omits children, use the target's
   app-server metadata list with `archived=true` and child sources to verify them.
   Do not reread unrelated retained tasks just to prove they were preserved.
4. Report individual successes and reasons, failures, unresolved records, and
   deferred candidates directly in the conversation. Distinguish automatically
   selected archives from user-confirmed ones; do not imply archival stopped work.
