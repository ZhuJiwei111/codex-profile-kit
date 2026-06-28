---
name: personal-brainstorms
description: Use before implementing new features, behavior changes, complex refactors, UI changes, or multi-step plans when goal, scope, acceptance criteria, brainstormed ideas, design tradeoffs, or implementation direction are not yet concrete.
---

# Personal Brainstorms

Clarify just enough before changing behavior. Do not turn simple edits into a
ceremony.

## Lock Before Editing

- Goal: what should be true when done.
- Scope: files/modules likely affected and explicit non-goals.
- Acceptance: commands, tests, UI states, or output artifacts that prove success.
- Risk: shared APIs, data migrations, user-visible behavior, long jobs, or
  credentials.

## Approach

- Prefer existing project patterns over new abstractions.
- If multiple approaches are plausible, state the tradeoff and choose the
  conservative path unless the user asked otherwise.
- Use the built-in plan tool for short multi-step work.
- Create persistent planning files only via `personal-planning-with-files-zh`.
- Treat plans shown to the user for confirmation, implementation, or handoff as
  user-facing text. Follow the user's language preference for that surrounding
  plan even when the plan is about generating Codex-facing artifacts such as
  `AGENTS.md`, `SKILL.md`, plugin metadata, or workflow notes.

## Lightweight Brainstorm

- Start with bounded local context: relevant instructions, manifests, entry
  points, nearby code, or examples. Skip broad scans when the likely edit
  surface is already clear.
- Shape the idea into goal, success criteria, constraints, and risks before
  proposing implementation work.
- Ask only questions that could change product behavior, output shape, data
  safety, dependency choice, environment, or acceptance criteria.
- When direction is open, offer 2-3 realistic approaches with tradeoffs and a
  recommended default. Keep the recommendation compatible with existing project
  patterns and the user's stated preferences.
- End with a compact plan or locked assumptions. Do not require a design doc,
  commit, worktree, or formal ceremony unless the user asks or the risk justifies
  it.

## Concern Discussion Mode

- Treat phrases such as `我的concern`, `讨论`, `不是命令`,
  `不一定要按我的`, `你觉得呢`, or similar uncertainty markers as a request for
  thought partnership rather than immediate execution.
- In this mode, first state your judgment, explain the relevant tradeoffs, name
  risks or hidden assumptions, and push back when the proposed direction seems
  unsafe, over-scoped, brittle, or inconsistent with the project.
- Offer 2-3 concrete options only when choices are genuinely live. Recommend a
  default, but keep it open for the user to revise.
- Convert concerns into one of: locked assumptions, a risk register, a decision
  checklist, or an implementation plan. Do not edit files or start jobs unless
  the user explicitly transitions from discussion to implementation.
- If the same prompt contains both a concern and an implementation request,
  clarify the plan/risk interpretation first; proceed only when execution intent
  and acceptance criteria are clear enough.

## Stop Conditions

- Ask the user before decisions that affect product behavior, data safety,
  credentials, installation, large downloads, long jobs, external publishing, or
  other high-risk outcomes.
- Ask when uncertainty would change the implementation direction, acceptance
  criteria, output shape, environment, dependency choice, or user-visible
  behavior.
- Make low-risk, local, easily reversible choices independently, and record the
  assumption when useful.
- The user is happy to help; do not guess brittle details just to appear
  autonomous.
