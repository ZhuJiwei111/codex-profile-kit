---
name: personal-task-archive
description: Manual only. Use when explicitly invoked to review or archive Codex chats within a user-selected scope. Does not clean files, retire skills, terminate jobs, or modify memory.
---

# Personal Task Archive

Use only by explicit invocation. An inventory or recommendation request is
read-only; an archive request authorizes the named targets or clearly completed
chats within the requested scope. Do not start periodic cleanup on your own.

## Scope

Use the user's selected chats, project, time range, and host. Default to the
calling host when none is named. A connected host may be selected explicitly;
keep each target's host identity with its ID throughout reads and mutations.
For named targets, inspect those targets without inventorying every chat.
For a broad cleanup, page the product metadata within that scope; disclose
incomplete coverage rather than presenting a partial list as a full inventory.
Read [inventory details](references/session-inventory.md) only when product
pagination, missing metadata, or runtime status needs interpretation.

## Decide From Actual Work

- For selection from a broad scope, keep the calling chat, running work, pinned
  or unread chats, active Goals/automations, unresolved user decisions, and
  ambiguous ownership out of the archive set.
- Completion means the requested result was delivered and no material work
  remains. Age alone does not establish completion; there is no mandatory
  24-hour delay, 15-day expiry, or fixed read-count cap.
- An optional next-step suggestion does not make completed work unfinished.
  Failure with an outstanding action does. An explicitly abandoned task or a
  source whose remaining work has an explicit successor may be archived.
- A finished subagent may be archived when its result was delivered to its
  parent. Parent metadata alone does not prove delivery, and an active parent
  does not by itself prevent child archival.
- If the user explicitly names a pinned or unread chat for archival, that
  selection overrides those organizational preferences. Known running work or
  a newly discovered ownership conflict needs discussion before proceeding.
- Missing metadata is unknown. Resolve only gaps that can change the decision;
  disclose unresolved gaps for a user-selected target without repeatedly asking
  for the same authority. A separate app-server's notLoaded status does not
  prove that execution stopped.

## Execute And Report

Use the native archive action only when explicitly authorized. Verify the latest
outcome and relevant execution status before mutation, reusing fresh evidence.
Archive exact host/ID pairs and verify the resulting archival state. Report links
such as [Title](thread://ID), the concrete reason, and any failures or unresolved
candidates. Report totals only when the inventory actually supports them.

Treat archival as organization: it does not stop, cancel, or prove completion of
jobs, delete history, or clean files. Do not copy a summary by default; archival
preserves the conversation. Use personal-multiline-coordination only when actual
remaining work needs an authorized ownership transfer. File scratch belongs to
personal-temporary-work; skill retirement belongs to profile maintenance.

Ordinary archival does not modify memory. Only if the user separately requests
memory work, read [memory hygiene](references/memory-hygiene.md). Never emulate
archival by moving history files or editing internal databases.
