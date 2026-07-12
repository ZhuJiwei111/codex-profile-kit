---
name: personal-brainstorms
description: Use to shape a bounded design before consequential feature, behavior, UI, refactor, or multi-step implementation decisions, and for explicit concern discussion; skip simple explicit low-risk edits.
---

# Personal Brainstorms

Turn consequential uncertainty into a bounded design through lightweight
dialogue. Do not add ceremony to simple, explicit, low-risk work.

## Scope Gate

Before detailed questions, use existing context and inspect only what is needed
to classify the request:

- **Direct handoff:** The goal, scope, acceptance, and implementation direction
  are concrete, and no consequential risk needs discussion. Yield to the
  appropriate implementation workflow without inventing alternatives or a
  second approval gate.
- **Bounded brainstorm:** One coherent change has unresolved consequential
  choices or risk assumptions. Use the workflow below.
- **Decompose first:** The request spans multiple independently deliverable
  subsystems. Name the units, their dependencies, and a recommended order.
  Brainstorm one bounded slice instead of refining the entire system at once.

If only `personal-grilling` is explicitly invoked, yield rigorous requirements
interrogation to that skill. If both skills are explicitly invoked, keep
brainstorming as the design coordinator and use grilling as the quality gate for
critical decisions.

If repository facts needed for the design are unclear, perform only bounded
inspection or use `personal-repo-intake`. Do not scan files or history by
default when the relevant context is already known.

## Composition With Personal Grilling

When both skills are invoked, brainstorming owns scope decomposition, evidence
synthesis, alternatives, recommendations, component boundaries, and final
design synthesis. `personal-grilling` owns critical-question admission, answer
lockability, and the blocking-decision gate.

Maintain a lightweight shared decision state only when it helps:

- `open`: material but not yet decided.
- `blocking`: planning would be unreliable without an answer.
- `locked`: fixed by the user or sufficient evidence.
- `assumption`: resolved with an explicit, low-risk, reversible default.
- `deferred`: intentionally outside the current delivery slice.

Do not require a formal decision table for lightweight work.

Before sending a question through the grilling gate, confirm that:

- The answer is not discoverable from available evidence.
- It would materially change scope, behavior, safety, cost, architecture,
  environment, output, or acceptance.
- A low-risk reversible default is not sufficient.
- The reason for deciding now can be stated.
- A recommended default and its material tradeoff can be offered.

Ask one blocking question at a time. After each answer, update the shared
decision state and the design instead of beginning a separate interview. Do not
repeat locked decisions, grill non-blocking implementation details, or run an
exhaustive checklist disconnected from the current design.

While a blocking decision remains unresolved, do not present the design as
ready for planning. When the grilling workflow releases its gate, return to
brainstorming for design synthesis, inline self-review, and the authorized
handoff.

## Workflow

1. **Frame the decision.** State the current goal, scope, non-goals, acceptance
   evidence, constraints, and material unknowns.
2. **Clarify selectively.** Ask only questions whose answers would change
   behavior, scope, safety, cost, environment, output, or acceptance. Ask one
   blocking question at a time. Do not ask facts discoverable from available
   evidence. When `personal-grilling` is also active, send candidate questions
   through its admission and lockability gate before asking the user.
3. **Compare real alternatives.** When multiple approaches are genuinely
   viable, present 2-3 with the recommendation first and explain the material
   tradeoff. If one path clearly fits, say why instead of inventing options.
4. **Present a bounded design.** Scale detail to complexity. For complex work,
   cover component responsibilities, interfaces and dependencies, data or
   control flow, failure behavior, and verification.
5. **Review the design inline.** Fix placeholders, contradictions, ambiguous
   requirements, unnecessary scope, weak component boundaries, and acceptance
   criteria that do not prove the requested outcome.
6. **Apply the execution gate.** Continue only according to the authorization
   already present in the request.

Prefer existing project patterns. Include a nearby structural improvement only
when it directly supports the requested outcome; do not turn the design into an
unrelated refactor.

For each significant component, be able to answer:

- What does it own?
- How do consumers use it?
- What does it depend on?
- Can its behavior be understood and tested without reading unrelated internals?

## Execution Gate

- For discussion or evaluation only, stop after the recommendation, decision,
  or bounded design. Discussion output is not implementation authorization.
- For a planning request, hand the locked design to the appropriate planning
  workflow, but do not infer implementation authority.
- For an explicit implementation request, brainstorming is a preflight rather
  than an automatic second approval gate. Continue within the original scope
  once material choices are lockable.
- If a question or presented alternative requires the user's decision, wait for
  the answer. Do not silently select an option after asking.
- When `personal-grilling` is active, an unresolved blocking decision overrides
  the ordinary handoff. Once its gate is released, preserve the authorization
  already present in the original request.
- Reopen only a new consequential decision; do not re-ask for an unchanged,
  already approved design.

Use the built-in plan for ordinary multi-step implementation. Use
`personal-planning-with-files-zh` only when file-backed, durable, or
cross-session planning is explicitly required. Do not create a design document,
worktree, commit, or persistent planning file merely because brainstorming ran.

## Concern Mode

`AGENTS.md` owns recognition of discussion signals. Once routed here:

- Lead with judgment, consequences, and a recommendation.
- Surface hidden assumptions and push back on unsafe, brittle, or over-scoped
  directions.
- Convert the concern into locked assumptions, a decision, a bounded risk list,
  or a design change.
- If the same request also authorizes implementation, resolve the material
  concern first and then follow the execution gate.

## Visual Assistance

Use the smallest visual only when relationships, sequence, state, layout, or
side-by-side options are materially clearer than prose:

- Use a table for exact mappings or tradeoffs.
- Use Mermaid for multi-component flow, hierarchy, or state transitions.
- Use a compact wireframe for layout decisions.

Keep textual requirements and ordinary technical choices in prose. Do not start
an external visual-companion server or create persistent visual artifacts unless
the user asks.

## Resources

Read `references/source-notes.md` only when auditing provenance or refreshing
this skill from upstream. It is not needed during an ordinary brainstorm.
