---
name: personal-brainstorms
description: Use to shape a bounded design before consequential feature, behavior, UI, refactor, or multi-step implementation decisions, and for explicit concern discussion; skip simple explicit low-risk edits.
---

# Personal Brainstorms

Turn consequential uncertainty into a bounded design. Keep this workflow light
enough to run implicitly; do not add a design ceremony to a simple, explicit,
low-risk change.

## Set The Boundary

- Use the request and bounded project evidence to state the goal, scope,
  non-goals, acceptance evidence, constraints, and consequential unknowns.
- Decompose work only when it contains independently deliverable parts. Choose
  one bounded slice and name dependencies on later slices.
- Inspect only facts that can change the design. Ask rather than guess when the
  answer changes behavior, safety, cost, compatibility, ownership, or visible
  acceptance.
- Treat discussion or concern signals as a request for judgment, not automatic
  implementation authority.

## Preserve Decision Continuity

For multi-round, cross-session, prior-task recovery, or handoff work, maintain
one canonical decision record. Use an existing project decision location when
one exists; otherwise name one exact task-owned Markdown path. Maintaining this
record is workflow bookkeeping, not implementation authority. If the active
action boundary explicitly forbids file writes, keep a complete inline snapshot
until persistent recording is allowed. Do not create competing ledgers.

Give each material entry a stable ID and record its status (`proposed`,
`locked`, `superseded`, `deferred`, or `open`), exact decision, source and
evidence cutoff, scope, consequences, dependencies, acceptance impact, and any
`supersedes`/`superseded_by` link. Keep observed facts, user decisions, agent
recommendations, and safe assumptions distinct; never promote a recommendation
to `locked` without an explicit user decision.

After each material answer, update the record before advancing: capture the
delta, detect conflicts with locked entries, obtain an explicit replacement
decision when needed, link the supersession, and propagate the result through
dependent scope, risks, interfaces, and acceptance. A later refinement may not
silently narrow, generalize, or reinterpret an earlier lock.

Before acting on “continue,” after context recovery or likely compaction, and
before synthesis or handoff, reload the canonical record and reconcile the
active locks, open branches, deferrals, and supersession chain. When persistent,
report its path and a revision or digest when practical.

## Shape The Design

1. Lead with the recommended direction and why it best fits the evidence.
2. When multiple approaches are genuinely viable, show two or three with the
   recommendation first and only the material tradeoffs.
3. Ask one consequential question at a time only when the user must choose.
   Never set `autoResolutionMs`, a timer, or an automatic default. Wait for the
   answer; silence, elapsed time, and UI expiry never select an option.
4. Present the smallest useful design. For complex work, cover component
   ownership, interfaces and dependencies, data or control flow, failure
   behavior, and verification.
5. Review the result inline for contradictions, hidden assumptions, scope
   creep, weak boundaries, and acceptance criteria that would not prove the
   requested outcome.

For a design synthesized from a decision record, give every material entry an
explicit disposition: preserved, translated into the design, explicitly
superseded, or explicitly deferred. Treat missing exact selectors, task-owned
semantics, failure behavior, risk disposition, and acceptance evidence as
losses, not harmless summarization. Do not replace task-specific contracts with
broader model or system defaults unless the record explicitly authorizes it.

Prefer established project patterns. Include a nearby structural improvement
only when it directly supports the requested outcome.

## Handle Concerns

- State the consequence and recommendation directly.
- Challenge unsafe, brittle, unnecessary, or over-scoped directions with
  concrete evidence.
- Convert the concern into a decision, locked assumption, bounded risk, or
  design change.
- If implementation was already authorized, continue only after the material
  concern is resolved and only within that original scope.

## Compose And Hand Off

`personal-grilling` owns exhaustive semantic coverage only when the user
explicitly invokes it. If both skills run, provide the design hypothesis and
defer its coverage confirmation to grilling; after confirmation, synthesize the
final design without repeating the interview. Consume the confirmed canonical
record as the design baseline and preserve its stable IDs and replacement
history through the handoff.

- For discussion only, stop with the recommendation or design and leave the
  canonical record current when one is active.
- For planning, hand the locked design to the requested planning workflow.
- For implementation, treat this as a preflight rather than a second approval
  gate; preserve the authority already present in the request.
- Use the built-in plan for ordinary multi-step work. Use
  `personal-planning-with-files-zh` only after explicit file-backed planning
  invocation.

Use a table, Mermaid diagram, or compact wireframe only when it materially
clarifies comparison, flow, hierarchy, state, or layout.

## Resource

Read [source-notes.md](references/source-notes.md) only for provenance or
maintenance.
