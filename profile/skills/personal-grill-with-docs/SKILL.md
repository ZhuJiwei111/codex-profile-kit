---
name: personal-grill-with-docs
description: Manual documented discussion workflow. Use when explicitly requested or when the user asks for a grilling session that maintains decisions and domain documentation across turns. Uses personal-grilling as the questioning core.
---

# Personal Grill With Docs

Read `../personal-grilling/SKILL.md` for questioning and completion rules.
This skill owns documentation and continuity, not a second interview algorithm.
Explicit invocation authorizes scoped local discussion records and relevant
domain documentation, not implementation, Git, external writes, or creation
of a project plan. When read by another workflow, inherit its existing authority.

## Choose The Existing Owner

Inspect relevant repository instructions and current documentation. Prefer the
user's named record, an existing discussion document, or a matching already-active
plan for current state. Do not create or select a project plan implicitly.
If no suitable owner exists, create one compact task-owned Markdown discussion
record in the established documentation location and report its path. Ask only
when location materially affects ownership or scope.

Keep current state separate from durable decisions. Use existing glossary and
ADR owners; read `../domain-modeling/SKILL.md` for conventions when terms or
architectural decisions need updating. Do not create competing ledgers or
copy the same state across documents.

## Maintain Useful State

At material decision boundaries, update only what changed:

- scope, non-goals, and settled decisions;
- evidence anchors for facts and explicit answers supporting decisions;
- open questions, consequential assumptions, and dependencies;
- superseded or deferred choices when needed to explain current state;
- the next material question or action.

Keep a compact record, not a transcript. User-owned choices remain open until
explicitly answered. Update a glossary when a meaningful term settles. Write an
ADR only for a consequential durable decision whose rationale future work needs,
not for every answer. Link durable owners rather than duplicating their content.

On continuation, compaction recovery, or handoff, reread state and linked decisions
before asking more questions. Reconcile new evidence and explicit user corrections
rather than treating old locks as immutable.

## Close

Apply the core's materiality-based finish rule. Reconcile the record with
conclusions, remaining assumptions, and the next action. No additional closure
approval is required. Continue an already-authorized next action; otherwise
present the concrete recommendation and identify the actual authority needed.
Do not automatically generate specs, tickets, or an implementation pipeline.
