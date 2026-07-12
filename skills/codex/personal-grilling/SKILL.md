---
name: personal-grilling
description: Manual only. Use $personal-grilling to pressure-test a plan or design with one decision-changing question at a time, research facts first, and block planning until material decisions are locked; pair with $personal-brainstorms for design synthesis.
---

# Personal Grilling

Pressure-test requirements with the fewest questions needed to make planning
reliable. Be rigorous, not exhaustive; direct, not theatrical or hostile.

## Contract

- Run only after explicit invocation. Do not turn ordinary ambiguity into a
  grilling session.
- Separate facts from decisions. Research discoverable facts before asking. Put
  every admitted material decision to the user and wait for the answer.
- Do not answer a material decision on the user's behalf merely because a
  plausible recommendation exists. Only a non-material, low-risk, reversible
  implementation detail may become an explicit `assumption`.
- Grill decisions, not generic themes. Every question must pass the admission
  gate below.
- Do not edit files, launch jobs, or implement while the grilling gate is
  active. After release, downstream workflows follow the original request's
  authorization.

## Question Admission

Ask only when all of these are true:

- The answer is neither already locked nor a fact discoverable from available
  evidence.
- It would materially change goal, scope, behavior, safety, cost, architecture,
  environment, output, or acceptance.
- It is needed before the current planning boundary and cannot be deferred.
- The item cannot be represented as a non-material, low-risk, reversible
  implementation assumption without changing the requested outcome.
- You can state why the decision matters now, a recommended default, and its
  material tradeoff.

If a candidate fails this gate, inspect the evidence, record an explicit
assumption, defer it, or omit it instead of questioning the user.

## Workflow

1. State the current hypothesis and build or reuse a decision state using
   `open`, `blocking`, `locked`, `assumption`, and `deferred`.
2. Order unresolved decisions by dependency and select the highest blocking one.
3. Ask one blocking question with the reason it matters, the minimum lockable
   answer, and a recommended default or 2-3 real options with tradeoffs. Wait for
   the answer before asking anything else.
4. Judge the answer against the exact decision. Lock it, record a safe default,
   defer it, or run the invalid-answer loop.
5. Update the decision state and repeat until no blocking item remains.

Ask exactly one admitted decision per turn. Do not set a numeric question limit.
Continue while admitted blocking decisions remain, and stop when every blocker
is locked or removed from the current scope, or when the user asks to stop. The
admission gate controls question quality; the question count does not define
completion.

If the user stops early, summarize `locked`, `assumption`, `deferred`, and
remaining `blocking` items without presenting the requirements as fully locked.

## Answer Discipline

A lockable answer resolves the current decision through an explicit choice,
default, measurable acceptance criterion, bounded scope, concrete constraint, or
evidence path. A blocking open question is a valid state, not a locked answer.

When an answer is not lockable, read
`references/answer-discipline.md`, name the exact failure, and re-ask the same
decision more narrowly. Do not move to a new theme or smooth over the gap.

## Composition With Personal Brainstorms

When both skills are invoked, accept the scope, evidence, alternatives, and
shared decision state from `personal-brainstorms`. Do not restart discovery or
repeat locked decisions.

Grilling owns question admission, answer lockability, and the blocking gate.
Brainstorming owns alternatives, component boundaries, and design synthesis.
When the gate is released, return the updated decision state to brainstorming in
the same turn.

## Gate And Handoff

While any `blocking` item remains:

- Do not produce an implementation plan, execution checklist, or ready claim.
- Continue with the next admitted question, or stop with:
  `阻断问题`, `阻断原因`, `最低所需答案`, `推荐默认`, and
  `擅自假设的风险`.

When no `blocking` item remains, produce the Chinese requirements brief below.
Release the grilling gate only when one of these is also true:

- The user confirms that the shared understanding is complete.
- The invoking request explicitly preauthorizes planning or implementation once
  every blocker is locked.

The second condition avoids asking for redundant confirmation after the user
already requested grilling followed by planning in the same turn. If neither
condition is satisfied, ask the user to confirm the brief and stop.

After release:

- When paired with `personal-brainstorms`, return the shared decision state for
  design synthesis and its authorized handoff.
- Otherwise, enter the appropriate planning workflow when the original request
  authorized planning or implementation.
- If no downstream work was requested, stop after the brief.
- Grilling itself does not edit, launch, or implement; the downstream workflow
  applies the original authorization boundary.

## Chinese Requirements Brief

Use these headings by default:

- **目标**
- **范围**
- **非目标**
- **验收标准**
- **关键决定**
- **默认与假设**
- **风险与回退**
- **未决问题**

Label every remaining item `blocking`, `non-blocking`, or `deferred`. Do not call
the brief locked while a blocking item remains. Follow an explicitly requested
language or format for the current session.

## Resources

Read `references/answer-discipline.md` only after an answer fails lockability or
when the precise failure taxonomy or blocking format is needed. Read
`references/source-notes.md` only when auditing provenance or refreshing this
skill from upstream.
