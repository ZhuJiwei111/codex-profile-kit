---
name: personal-task-archive
description: Use when Codex tasks accumulate on one host, completed or superseded tasks need archival, archive eligibility is uncertain, or ongoing traffic needs archive-versus-runtime triage.
---

# Personal Task Archive

Organize tasks on the execution host. Archive clear cases automatically when
the request authorizes archival, and leave recent or ambiguous work to the
user.

## Current-Host Boundary

- Identify the calling task's current host before any task query. Use that same
  exact host identity for every list, read, message, and archive operation.
- Scope the entire run to the current execution host. A user naming another
  host does not expand this run; manage that host from a task executing there.
- Use the current host's native shell and filesystem conventions. Resolve its
  own `CODEX_HOME`; never reuse a path, index, or shell command from another
  platform.
- Derive mutation authority from the request. Treat audit, review, inventory,
  and recommendation requests as read-only. Treat an explicit request to
  archive eligible tasks as authority to archive clear cases without another
  confirmation; ask the user only about uncertain cases or user-owned choices.
- Archive tasks through the product action; never delete or move task history
  files to emulate archival.
- Protect the calling task, running tasks, Goals, automations, unread tasks,
  pinned tasks, ambiguous tasks, and an explicitly identified main task.
- Read only bounded metadata and task summaries. Keep auth/session payloads,
  raw transcripts, SQLite, attachments, caches, logs, rollout JSONL, and
  unrelated tool output outside the workflow.
- Submit approved memory changes through a new timestamped ad-hoc note; leave
  generated memory files unchanged.

## Choose The Operation

- For accumulated tasks or a periodic review, run the bounded current-host
  inventory below.
- For unexpected ongoing traffic, identify whether a command, Goal,
  automation, retry loop, or host runtime is still active. Treat archival as
  organization, not evidence that execution or traffic stopped. Complete the
  relevant runtime diagnosis first, then return here for archival.
- For only the calling task's final closeout, use
  `personal-thread-closeout`; do not run a multi-task inventory.
- For memory review or preservation, use the Memory Hygiene branch only after
  the user explicitly requests it.

## Classification Rules

Apply hard protection before age or convenience. A task with material
unfinished work, an unresolved user choice, ambiguous ownership, or any other
protected state is not an automatic archive.

Measure age from the last substantive user request or work result. Archive,
unarchive, rename, pin, and other maintenance events do not reset that age.
When only a generic update time is available, use it conservatively rather
than inventing an older substantive date.

| Evidence | Action |
| --- | --- |
| Completed less than 24 hours ago | Temporarily protect without asking. |
| Completed 24 hours to 15 days ago and clearly lightweight | Archive automatically when authorized. |
| Completed 24 hours to 15 days ago but not clearly lightweight | Ask the user with a task link and one-sentence summary. |
| Completed more than 15 days ago | Archive automatically when authorized after the hard-protection check. |
| Another task already explicitly owns all remaining work | Archive the source automatically after any necessary handoff. |
| A finished subAgent already delivered its result, or its parent explicitly owns all remaining work | Archive automatically when authorized, regardless of age. |
| A subAgent is running, awaiting delivery, missing its parent, or otherwise ambiguous | Protect or ask. |
| Failed with a material next action | Protect or ask; failure is unfinished work. |
| Closed failure that the user abandoned, terminated, or moved to an explicit successor | Archive automatically when authorized. |

The explicit-successor and closed-failure rows override the age windows. They
do not override hard protection such as the calling task, a running task, an
automation, or a pinned task.

Treat a task as lightweight only with positive evidence: it has one routine or
independent outcome, that outcome is verified, it has no material next action,
and its conversation has little continuing design, implementation, diagnostic,
or reference value. Optional post-completion suggestions do not create a
material next action. If lightweight status is unclear, review it with the
user.

Treat succession as explicit only when the user, source task, or successor task
already identifies the successor and the successor actually owns the remaining
work. Similar titles, a newer task in the same category, or a summary sent
during archival do not establish ownership. Copying a summary alone does not
transfer ownership.

Classify a thread as a subAgent only from product source or parent metadata,
never from its title. A confirmed finished subAgent is subordinate work rather
than an independent recent task: once its result is delivered to the parent, or
the parent explicitly owns the remaining work, archive it without the ordinary
24-hour delay. Preserve every hard protection, especially running, unread,
pinned, undelivered, and ambiguous subAgents. Archival organizes history; it
does not stop, cancel, or prove completion of a subAgent.

Treat parent archival state and child completion as separate facts. An
unarchived parent does not protect a finished, delivered subAgent; it often
remains active while it owns the integrated result and subsequent work. A
parent ID alone is not delivery evidence. Confirm delivery or explicit
ownership from product metadata or a bounded exact read before automatic
archival.

A task that the user unarchives during the current cleanup is protected for the
rest of that run. Use pinning for durable protection across later cleanups; do
not create a hidden archive-exclusion list.

## Build A Bounded Current-Host Inventory

1. Resolve the current host identity and freeze it as the scope for this run.
2. Acquire a complete host-local metadata list. Prefer a product query that
   applies the frozen host filter before returning data, exposes source or
   parent metadata, and pages to exhaustion. Otherwise use the local app-server
   metadata path in [current-host inventory](references/session-inventory.md).
3. Verify that pagination completed and record the inventory source. Treat an
   app-wide, capped, cross-host, or child-omitting list as navigation only, not
   as the inventory. A host filter applied after such results arrive does not
   make the list complete.
4. Project bounded metadata and report the raw unarchived main-task and
   subAgent totals before exclusions. Then report protection exclusions,
   eligible candidates, read candidates, and deferred candidates as
   distinct counts; never label a candidate count as a host total.
5. Exclude the calling task and metadata-known running, automation, Goal,
   pinned, unread, and less-than-24-hours-old tasks before deep reads; retain
   finished-and-delivered subAgents as age-independent candidates.
6. Sort remaining candidates oldest first. Deep-read at most 50 tasks in one
   normal run. A user-requested complete inventory may continue in batches.
7. Resolve only those candidates through exact reads on the frozen host. Treat
   `No Codex thread found` as an index-only child, stale entry, or
   unsupported record. Record it once; do not retry it as a mutation.
8. Collect the latest substantive outcome, required next action, ownership,
   and enough context to distinguish lightweight from continuing work.
9. Split results into automatic archives, temporary or hard protection, and
   user review. Report whether more candidates remain beyond the 50-task cap.

An incomplete, unfiltered, or cross-host product API is not archive authority.
If the current-host identity or a material safety signal cannot be resolved,
keep that candidate out of automatic execution.

## Review With Links

Do the classification work for the user. For each review item, provide a
clickable `[@Title](thread://ID)` link followed by one sentence summarizing its
state and the recommended action. If a reliable summary is unavailable, link
the task and say that its state is unknown. When succession matters, link both
the source and successor.

Report each automatic archive with its link and one specific reason. Do not
combine materially different reasons into an "or" statement. Accept user
corrections by title or ID.

## Execute Authorized Archives

1. Re-read every eligible target with the frozen host identity immediately
   before mutation. If its status, pin, unread state, automation role, material
   next action, or ownership changed, move it to protection or user review.
2. Do not copy a summary by default. Task archival preserves the task history.
   Send a minimal handoff only when an explicit successor already owns the work
   and lacks information required to continue; verify delivery before archival.
3. Archive only exact IDs within the authorized host and task scope.
4. Verify the tasks actually archived. Do not re-read every protected or main
   task merely to prove that it was not archived.
5. Report individual success, failure, and missing records, plus any candidates
   deferred by the 50-task cap.

## Memory Hygiene

Ordinary archival does not modify memory. Read
[memory hygiene](references/memory-hygiene.md) only when the user explicitly
asks to audit or change memory.

1. Inventory safe generated files and topic headings on the current host.
2. Classify stable preferences, reusable workflows, provenance, duplicates,
   stale live facts, and contamination.
3. Propose keep, merge, compact, delete, or provenance-only decisions.
4. After explicit approval, create one small timestamped note under the
   current host's `~/.codex/memories/extensions/ad_hoc/notes/`.
5. Report the note as submitted and pending regeneration.
6. Verify regeneration only in a fresh task on that same host.

## Completion Report

Report the current-host identity, automatically archived task links with
individual reasons, raw unarchived main-task and subAgent totals, protection
exclusions, eligible and deferred candidate counts, linked review items with
one-sentence summaries, missing records, and any product-tool limitation.
Report memory work only when that branch was explicitly requested.
