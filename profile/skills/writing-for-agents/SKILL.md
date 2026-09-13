---
name: writing-for-agents
description: Write or revise agent-facing instructions, including skills, AGENTS.md, and CLAUDE.md.
---

# Writing For Agents

Give the agent the outcome, relevant context, decision boundaries, and a
checkable completion condition. Assume it can choose ordinary implementation
steps. Preserve user preferences, domain facts, and operational constraints
that would not be obvious from the task or environment.

When writing a skill, use [SKILL-MECHANICS.md](SKILL-MECHANICS.md) for Codex
frontmatter, invocation policy, and reference routing.

## Scope And Decisions

Separate binding constraints from recommendations and examples. State when a
rule applies and what consequence requires stopping. Reuse existing task
authority; ask only about unresolved choices that materially change the result
or an action whose authority is missing. If a rule would block requested work,
make the exact rule and its applicability visible to the user.

Specify required order when correctness depends on it. For ordinary work,
describe success and let the agent choose the route. Replace blanket reading,
confirmation, test, and review requirements with their actual triggers. Keep
fragile procedures, schemas, security boundaries, and explicit user gates exact.

## Discovery And Context

A skill description or document pointer should identify its capability and
when it is useful. Keep distinct triggers; remove synonym lists and broad
catchalls that pull unrelated tasks into the workflow. Put detailed modes and
examples in the body, not the always-loaded description.

Keep shared purpose and essential boundaries in the entrypoint. Disclose
substantial branch-specific guidance through a link that says when to read it.
A short, self-contained skill needs no router. Preserve reference paths and
load only material needed for the current branch.

Keep each rule with its context and exceptions in one authoritative owner.
Reference environment-owned facts instead of copying cheap lookups into prose.
Use the project's familiar terms; introduce a new term only when it clarifies
an actual distinction. Prefer positive target behavior, retaining explicit
prohibitions where they express real authorization or safety boundaries.

## Completion And Validation

Define completion by the requested result and proportionate evidence. A first
implementation is not complete when applicable checks or cause-backed fixes
remain. Passing checks need no repetition without new changes or concerns.

Review the final instructions for conflicting routes, accidental authority
expansion, hidden approval gates, and broken references. Use realistic requests
to assess a substantial behavior change when such validation is authorized;
schema checks alone do not establish model behavior. Remove obsolete or
redundant guidance, but do not delete a real constraint merely to shorten text.
