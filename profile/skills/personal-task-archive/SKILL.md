---
name: personal-task-archive
description: Audit, group, consolidate, and archive Codex tasks on the current execution host across Windows, macOS, or Linux. Use when tasks pile up, the user is unsure what to archive, completed or superseded tasks need review, continued traffic needs archive-versus-runtime triage, a periodic current-host inventory is requested, or durable context and memory must be preserved before archival.
---

# Personal Task Archive

Organize tasks and preserve durable context on the host where this skill is
running without inspecting or mutating another connected host.

## Current-Host Boundary

- Identify the calling task's current host before any task query. Use that same
  exact host identity for every list, read, message, and archive operation.
- Scope the entire run to the current execution host. A user naming another
  host does not expand this run; manage that host from a task executing there.
- Use the current host's native shell and filesystem conventions. Resolve its
  own `CODEX_HOME`; never reuse a path, index, or shell command from another
  platform.
- Use two phases: read-only inventory and proposal, then exact mutation after
  explicit confirmation.
- Archive tasks through the product action; never delete or move task history
  files to emulate archival.
- Protect the calling task, running tasks, Goals, automations, unread or
  ambiguous tasks, and every selected main task.
- Read only bounded metadata and task summaries. Keep auth/session payloads,
  raw transcripts, SQLite, attachments, caches, logs, rollout JSONL, and
  unrelated tool output outside the workflow.
- Submit approved memory changes through a new timestamped ad-hoc note; leave
  generated memory files unchanged.

## Choose The Operation

- For accumulated tasks or a periodic review, run the full current-host
  inventory and retain one main task per work type.
- For unexpected ongoing traffic, identify whether a command, Goal,
  automation, retry loop, or host runtime is still active. Treat archival as
  organization, not evidence that execution or traffic stopped. Complete the
  relevant runtime diagnosis first, then return here for archival.
- For only the calling task's final closeout, use
  `personal-thread-closeout`; do not run a multi-task inventory.
- For memory review or preservation, use the Memory Hygiene branch only after
  the user explicitly requests it.

Task age and task count may trigger a review, but never make a task eligible
for automatic archival. If the user wants help remembering, propose a
low-frequency reminder as a separate action with its own cadence and
authorization. Keep every archive decision reviewable.

## Archive Eligibility

Propose a task for archive only when it is completed or clearly superseded,
has no live command, Goal, automation, retry, unread result, unresolved user
choice, or ambiguous ownership, and any durable conclusions or open work have
been consolidated into the selected main task or canonical project document.
Keep uncertain tasks protected.

## Phase 1: Build A Current-Host Inventory

1. Resolve the current host identity and freeze it as the scope for this run.
2. Seed candidate IDs from a product query that guarantees current-host
   filtering before results enter context. If unavailable or incomplete, use
   the safe metadata procedure in
   [current-host inventory](references/session-inventory.md).
3. Resolve candidates through exact task reads using the frozen host identity.
4. Treat `No Codex thread found` as an index-only child, stale entry, or
   unsupported record. Record it once; do not retry it as a mutation.
5. Group tasks by work type, such as maintenance, connectivity, research,
   documents, development, and recurring operations.
6. Select one main task per work type from current activity, completeness,
   recency, unresolved work, and user preference. Do not choose one global
   main task.
7. Present exact IDs for main, protected, archive-only, and uncertain tasks,
   plus every evidence gap.
8. Stop for explicit confirmation of the exact mutation list.

An incomplete, unfiltered, or cross-host product API is not archive authority.
If current-host status cannot be resolved safely, keep the candidate protected.

## Phase 2: Consolidate And Archive

1. Re-read every approved target with the frozen host identity immediately
   before mutation. Stop if status, unread state, automation role, or ownership
   changed.
2. Read only the bounded summaries needed to preserve durable conclusions,
   open actions, risks, and dated facts.
3. Send one consolidation message to the selected current-host main task.
   Include source IDs and titles, durable conclusions, unresolved actions, and
   stale facts marked historical.
4. Verify that the message was accepted before archiving source tasks.
5. Archive only the confirmed exact IDs. Report success, failure, and missing
   records individually.
6. Verify every protected, main, and archived task through exact current-host
   reads. Do not use an app-wide count as proof.

Codex does not splice histories. "Merge" means writing a compact provenance
summary into the selected main task and then archiving reviewed sources.

## Memory Hygiene

Read [memory hygiene](references/memory-hygiene.md) only when the user
explicitly asks to audit or change memory.

1. Inventory safe generated files and topic headings on the current host.
2. Classify stable preferences, reusable workflows, provenance, duplicates,
   stale live facts, and contamination.
3. Propose keep, merge, compact, delete, or provenance-only decisions.
4. After explicit approval, create one small timestamped note under the
   current host's `~/.codex/memories/extensions/ad_hoc/notes/`.
5. Report the note as submitted and pending regeneration.
6. Verify regeneration only in a fresh task on that same host.

## Completion Report

Report the current-host identity, main task retained per work type, exact
consolidated and archived IDs, protected and unresolved records, notes created,
regeneration status, and any product-tool limitation.
