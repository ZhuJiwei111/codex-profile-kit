---
name: personal-grilling
description: Manual only. Use $personal-grilling to pressure-test a plan or design one theme at a time, opening each theme with one guided neutral question before narrowing decisions, with no timeout and with coverage, consistency, adversarial, risk, and explicit-confirmation closure.
---

# Personal Grilling

Run a coverage-first requirements interrogation before consequential planning or
implementation. Optimize for a sourced, consistent, adversarially tested state,
not the fewest questions. Be rigorous without becoming hostile or theatrical.

## Contract

- Run only after explicit invocation. Keep implicit invocation disabled.
- Treat the proposed solution as a hypothesis. Test problem framing, necessity,
  smaller alternatives, hidden coupling, second-order effects, and failure.
- Separate facts from decisions. Investigate discoverable facts; put every
  material user-owned decision to the user and wait.
- Work on one material theme at a time. Open each new theme with exactly one
  neutral, guided open-ended question before recommendations or solution
  options.
- Make the opening answerable: state why the answer matters, add three to five
  explicitly non-exhaustive reference angles, and give a minimum-effort response
  shape such as choosing one angle, rewriting it, or saying none fits.
- Keep opening scaffolding neutral. Reference angles may name dimensions,
  incidents, constraints, failure signals, or answer forms, but must not smuggle
  in a recommended decision, pretend to be exhaustive, or auto-select an answer.
- When the user expresses uncertainty or asks for reference, examples, or a
  recommendation, do not repeat the open-question loop. Give an evidence-backed
  recommendation and no more than three real alternatives with tradeoffs, then
  accept a number, “use the recommendation,” a rewrite, or “none fit.”
- After the opening answer, ask exactly one material decision per user turn. Set
  no session question cap.
- Questions have no timeout and never auto-resolve. Silence, elapsed time, a UI
  expiry, or a tool default is not an answer. Wait until the user answers,
  explicitly defers, pauses, or stops.
- Do not edit, launch, or implement while the gate is active. Bounded,
  decision-relevant read-only evidence collection remains allowed.
- Keep the ledger in the conversation unless another workflow explicitly owns
  persistence.

A decision is material when it can change the goal, scope, behavior,
architecture, data or state, dependencies, safety, compatibility, cost,
resources, operations, rollback, acceptance, or likely rework. Only a
non-material, low-risk, reversible detail may become an assumption.

## Build Themes And Coverage

Before the first question, read
[coverage-model.md](references/coverage-model.md). Build themes and leaves from
its universal core, every applicable task pack, observed evidence, dependencies,
user answers, and risks.

Account for every core dimension before filtering questions. Close leaves with
sufficient evidence, inherited constraints, a safe assumption, explicit user
deferral, or justified `not-applicable`. Only unresolved material user-owned
leaves become questions. Every theme and leaf retains status; every leaf also
retains provenance, dependencies, consequence, and material risk disposition.

## Investigate Decision-Changing Facts

At the start and between themes, inspect scoped code, config, tests, docs,
necessary Git history, runtime facts, or authoritative sources when the result
can change a branch or recommendation.

- Distinguish `observed`, `inference`, and `unknown`.
- Reuse a deterministic source or failure until a material precondition changes.
- Do not enumerate unrelated repositories, tasks, sessions, memories, hosts, or
  credentials, and never expose secret values.
- Stop when more evidence would no longer change a decision, risk, or acceptance
  criterion.

## Open-Then-Narrow Theme Loop

1. Select the unresolved material theme with the highest safety, dependency, or
   rework impact.
2. If it is unopened, state why it matters and ask one neutral, guided
   open-ended question. Include non-exhaustive reference angles and a
   minimum-effort response shape, but no recommendation, preferred default,
   solution menu, or proposed final answer.
3. Wait without a timeout. Classify the answer, discover its leaves, and inspect
   decision-changing facts. If the answer expresses uncertainty or asks for
   reference, use the recovery contract in
   [answer-discipline.md](references/answer-discipline.md) instead of asking
   another open question by default.
4. For each remaining material user-owned leaf, state the minimum lockable
   answer. Only after the open answer may you offer a recommendation or two or
   three real alternatives with material tradeoffs.
5. Ask only that decision and wait without auto-resolution.
6. Lock only the answered leaf. Use
   [answer-discipline.md](references/answer-discipline.md) when it is not
   lockable.
7. Propagate the answer through dependencies, risks, acceptance, and task packs;
   open or reopen newly material leaves.
8. Report a concise delta: what locked, what appeared, whether the theme can
   close, and why the next question has priority.

An unambiguous `1`, `yes`, or “use the recommendation” resolves the presented
choice without a fabricated rationale. It does not close the entire theme.
Close a theme only after its material leaves and consequences are dispositioned.
New evidence reopens only affected leaves and dependent closure evidence.

## Assumptions, Deferral, And Risks

- A material item may be deferred only through an explicit user choice.
- `not-applicable` requires evidence that the dimension cannot affect this slice.
- An assumption must be non-material, low-risk, reversible, small in blast
  radius, and unable to alter material acceptance.
- Every material residual risk requires `avoid`, `mitigate`, `accept`, or
  `defer`. Recording a risk is not acceptance.

## Composition With Personal Brainstorms

When both skills are invoked, brainstorming is the sole design-synthesis owner.
Grilling independently opens themes, audits coverage, and may reopen weak,
contradictory, or missing decisions. It does not emit a parallel design, plan,
recommendation synthesis, or ready claim.

Reuse sufficient evidence, but do not assume brainstorming's selective
clarification found every branch. After explicit coverage confirmation, return
only the sourced ledger and gate status to brainstorming for synthesis and the
authorized handoff.

## Three-Pass Closure

Do not infer completion from `blocking == 0`. After the last material answer,
run these passes in order:

1. **Coverage pass:** every universal dimension, applicable pack, derived branch,
   theme, and material risk has justified status, provenance, and consequence.
2. **Consistency pass:** decisions, evidence, dependencies, scope, constraints,
   and acceptance agree; late choices have propagated.
3. **Adversarial pass:** challenge framing, failure and recovery, security,
   compatibility, migration, operations, ownership, second-order effects,
   rollback, and whether acceptance can prove the outcome.

Any material gap resumes the open-then-narrow loop at the affected theme. Do not
bundle newly discovered decisions into a final questionnaire.

## Explicit Coverage Confirmation

After all three passes succeed, show a complete but proportionate ledger. Retain
every material leaf while grouping evidence-backed non-material or
not-applicable details by dimension. Include assumptions, deferrals,
not-applicable reasons, risk dispositions, and accepted method limitations.
Ask the user to confirm coverage completeness, and wait without a timeout.

Confirmation is required even after preauthorization. It confirms requirements,
not implementation authority. Preserve original same-scope authorization after
confirmation. A new material concern reopens affected leaves and closure
evidence.

## Stop And Handoff

While the gate is active, do not present an implementation plan, checklist, or
ready claim. If the user stops, return an incomplete requirements ledger with
locked decisions, evidence, assumptions, deferrals, risks, and blockers.

After confirmation, return the ledger to `personal-brainstorms` when paired. If
grilling ran alone, return a requirements ledger rather than synthesizing a
design; route a requested design synthesis to brainstorming. Enter another
workflow only when the original request authorized it.

Use Chinese by default. A compact ledger should cover goal and owners, evidence,
scope and behavior, state and interfaces, constraints and acceptance, decisions
and sources, assumptions and deferrals, risks, and unresolved items.

## Resources

- [coverage-model.md](references/coverage-model.md): theme and leaf discovery,
  task packs, ordering, and closure passes.
- [answer-discipline.md](references/answer-discipline.md): guided open-first,
  uncertainty recovery, examples, and lockable-answer rules.
- [source-notes.md](references/source-notes.md): provenance and local decisions.
