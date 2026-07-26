---
name: personal-reconcile-decisions
description: Manual only. Use only when the user explicitly invokes this skill to recover current working context from, or review material decisions in, named Codex task histories, exported task turns, and an existing canonical document; distinguish user locks, observed facts, agent proposals, superseded items, and open questions without implementing the work.
---

# Personal Reconcile Decisions

Reconstruct the current decision state from only the tasks, exports, and
canonical document named by the user. Do not scan unrelated tasks, another
host, memory, or the whole project by default.

## Reconcile Sources

Read enough source turns to resolve material decisions and their order. Treat
forked copies of parent history as duplicate evidence, not independent votes.

Classify only result-changing material as:

- user-locked;
- observed fact with evidence cutoff;
- Codex proposal or inference;
- superseded or deferred; or
- open.

A later explicit user answer may supersede a canonical document. Fresh
repository evidence may make an old observed fact stale, but it does not
replace a user decision. Never promote an unanswered recommendation to a lock.

## Return Current State

Default to a compact inline result. Make the current objective, active locks,
material conflict or gap, open user choice, evidence cutoff, and exact next
action discernible without replaying the timeline. A review request may stop at
the audited conclusion rather than producing a continuation.

Update a file only when the user explicitly asks, and then revise the one named
canonical document in place. Do not create a competing ledger, transcript,
matrix, or additional plan.

Do not continue design, implement, archive tasks, perform Git, publish, or take
another external action. Grilling owns its own live decision record; project
file planning, App-task coordination, and task closeout retain their separate
owners.
