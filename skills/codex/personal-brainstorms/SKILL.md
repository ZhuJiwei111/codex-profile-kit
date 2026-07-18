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
final design without repeating the interview.

- For discussion only, stop with the recommendation or design.
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
