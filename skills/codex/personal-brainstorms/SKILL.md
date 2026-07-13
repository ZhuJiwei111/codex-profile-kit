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

The direct-handoff and lightweight classification above govern brainstorming
when it runs alone. They do not release a simultaneously invoked
`personal-grilling` gate; in the paired workflow, provide the initial
decomposition and enter its coverage audit.

If only `personal-grilling` is explicitly invoked, yield rigorous requirements
interrogation to that skill. If both skills are explicitly invoked, keep
brainstorming as the design coordinator and use grilling as an independent
coverage gate over the shared decision tree.

If repository facts needed for the design are unclear, perform only bounded
inspection or use `personal-repo-intake`. Do not scan files or history by
default when the relevant context is already known.

## Composition With Personal Grilling

When both skills are invoked, brainstorming owns initial scope decomposition,
evidence synthesis, alternatives, recommendations, component boundaries, and
final design synthesis. `personal-grilling` independently owns coverage-tree
construction, answer lockability, material-risk disposition, the three closure
passes, and the explicit coverage-confirmation gate.

Brainstorming supplies its current design hypothesis and decision state; it
does not certify that the state is complete. Grilling may reopen a decision
when coverage, evidence, dependency propagation, consistency, or adversarial
review exposes a material gap. It should reuse sufficient evidence and avoid
repeating an unchanged, already supported leaf.

Maintain one shared sourced ledger while grilling is active. Brainstorming must
not filter out a material branch merely because its solo workflow would use a
lighter clarification standard. Not every covered dimension becomes a user
question: grilling closes discoverable facts, inherited constraints, safe
non-material assumptions, explicit deferrals, and justified not-applicable
branches under its own contract.

Ask one material decision at a time. After each answer, update the shared
ledger and propagate consequences into the design instead of beginning a
second interview. While the grilling coverage gate remains active, do not
present the design as ready for planning. After its three closure passes and
explicit user confirmation, return to brainstorming for synthesis, inline
self-review, and the authorized handoff.

## Workflow

1. **Frame the decision.** State the current goal, scope, non-goals, acceptance
   evidence, constraints, and material unknowns.
2. **Clarify selectively.** When brainstorming runs alone, ask only questions
   whose answers would change behavior, scope, safety, cost, environment,
   output, or acceptance. Ask one blocking question at a time and do not ask
   discoverable facts. This lightweight selective-question rule does not apply
   while `personal-grilling` is active; provide the current decomposition and
   let its coverage model discover, classify, and sequence material leaves.
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
- When `personal-grilling` is active, its coverage gate overrides the ordinary
  handoff. Require its explicit coverage confirmation even when implementation
  was preauthorized; after release, preserve the authorization already present
  in the original request instead of asking for it again.
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
