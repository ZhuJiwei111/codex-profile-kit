---
name: personal-grilling
description: Manual only. Use $personal-grilling to pressure-test a plan or design through coverage, consistency, and adversarial closure, asking one material decision at a time and blocking handoff until every material branch and residual risk is explicitly dispositioned.
---

# Personal Grilling

Run a coverage-first requirements interrogation before consequential planning or
implementation. Optimize for a sourced, internally consistent, adversarially
tested decision state—not the fewest questions. Be rigorous and direct without
becoming hostile or theatrical.

## Contract

- Run only after explicit invocation. Keep implicit invocation disabled.
- Treat the proposed solution as a hypothesis. Test the problem framing,
  necessity, smaller alternatives, hidden coupling, second-order effects, and
  failure conditions.
- Separate facts from decisions. Investigate discoverable facts; put every
  material user-owned decision to the user and wait.
- Ask exactly one material decision per user turn. Set no session question cap.
- Do not edit, launch, or implement while the gate is active. Bounded,
  decision-relevant read-only evidence collection remains allowed.
- Keep the ledger in the conversation by default. Do not create persistent
  state merely because grilling is long.

A decision is material when it can change the goal, scope, behavior,
architecture, state or data contract, dependencies, safety, compatibility,
cost, resources, operations, rollback, acceptance, or likely rework. Only a
non-material, low-risk, reversible detail may become an assumption.

## Build Coverage Before Filtering

Before the first question, read
[coverage-model.md](references/coverage-model.md). Build a tree from its
universal core, every applicable task-type pack, observed evidence, dependency
edges, user answers, and risks.

Account for every core dimension before deciding what to ask. Close leaves with
sufficient evidence, inherited constraints, a safe assumption, explicit user
deferral, or a justified `not-applicable` result. Only unresolved material
user-owned leaves become questions. Every leaf must retain status, provenance,
dependencies, consequence, and any material risk disposition.

## Investigate Decision-Changing Facts

At the start and between themes, inspect scoped code, config, tests, docs,
necessary Git history, runtime facts, or authoritative external sources when
the result can change a branch or recommendation.

- Distinguish `observed`, `inference`, and `unknown`.
- Reuse a deterministic source or tool failure until a material precondition
  changes.
- Do not enumerate unrelated repositories, tasks, sessions, memories, hosts,
  or credentials, and never expose secret values.
- Stop when more evidence would no longer change a decision, risk, or acceptance
  criterion.

## One-Decision Loop

1. Select the unresolved material leaf with the highest dependency or rework
   impact.
2. State why it matters and the minimum lockable answer.
3. Offer a recommended default or two or three real alternatives with their
   material tradeoff.
4. Ask only that decision and wait.
5. Lock only the answered leaf. Use
   [answer-discipline.md](references/answer-discipline.md) for an unlockable
   answer.
6. Propagate the choice through dependencies, consequences, risks, acceptance,
   and task packs. Open or reopen newly material leaves.
7. Report a concise delta: what locked, what branch appeared, and why the next
   question now has priority.

An unambiguous `1`, `yes`, or “use the recommendation” resolves the exact
choice without requiring a fabricated rationale. It does not close the entire
theme. New evidence or a concern reopens only affected leaves and invalidates
only closure evidence that depended on them.

## Assumptions, Deferral, And Risks

- A material item may be deferred only through an explicit user choice.
- `not-applicable` requires evidence that the dimension cannot affect this
  delivery slice.
- An assumption must be non-material, low-risk, reversible, small in blast
  radius, and unable to alter material acceptance.
- Every material residual risk requires `avoid`, `mitigate`, `accept`, or
  `defer`. Merely recording a risk is not acceptance.

## Composition With Personal Brainstorms

When both skills are invoked, brainstorming owns initial decomposition,
alternatives, component boundaries, and final synthesis. Grilling independently
audits coverage and may reopen weak, contradictory, or missing decisions.

Reuse sufficient evidence, but do not assume brainstorming's selective
clarification found every material branch. Brainstorming must not filter out a
material branch merely because its solo workflow would stay light. After
explicit coverage confirmation, return the sourced ledger for synthesis and
the authorized handoff.

## Three-Pass Closure

Do not infer completion from `blocking == 0`. After the last material answer:

- **Coverage pass:** every universal dimension, applicable pack, derived
  branch, and material risk has a justified status, provenance, and consequence.
- **Consistency pass:** decisions, evidence, dependencies, scope, constraints,
  and acceptance agree; late choices have propagated.
- **Adversarial pass:** challenge problem framing, failure and recovery,
  security, compatibility and migration, operations, ownership, second-order
  effects, rollback, and whether acceptance evidence can actually prove the
  outcome.

Any material gap resumes the one-decision loop. Do not bundle newly discovered
decisions into a final questionnaire.

## Explicit Coverage Confirmation

After all three passes succeed, show a complete but proportionate ledger:
retain every material leaf while grouping evidence-backed non-material or
not-applicable details by dimension. Include assumptions, deferrals,
not-applicable reasons, risk dispositions, and accepted method limitations.
Ask the user to confirm coverage completeness.

Explicit coverage confirmation is required even after preauthorization. It
confirms requirements, not implementation authority. After confirmation,
preserve any original same-scope authorization instead of asking again. A new
material concern reopens affected leaves and the relevant closure evidence.

## Stop And Handoff

While the gate is active, do not present an implementation plan, execution
checklist, or ready claim. If the user stops early, return an **incomplete
requirements brief** with locked decisions, evidence, assumptions, deferrals,
risk dispositions, and blockers.

After confirmation, return the ledger to `personal-brainstorms` when paired;
otherwise enter a downstream workflow only when the original request authorized
it. Stop after the brief when no downstream work was requested.

Use Chinese by default. A compact brief should cover:

- **目标、问题、用户与责任人**
- **当前证据**
- **范围、非目标、行为、状态与接口**
- **约束、兼容、运维与验收**
- **关键决定及来源**
- **默认、假设、延期与不适用项**
- **风险、处置与未决问题**

## Resources

- Read [coverage-model.md](references/coverage-model.md) before constructing the
  tree and when a new task type appears.
- Read [answer-discipline.md](references/answer-discipline.md) when an answer or
  closure status is not lockable.
- Read [source-notes.md](references/source-notes.md) only for provenance or
  maintenance.
