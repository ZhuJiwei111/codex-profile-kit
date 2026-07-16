# Answer And Closure Discipline

Use this reference when an answer, leaf status, deferral, risk disposition, or
closure claim is not strong enough to enter the sourced coverage ledger.

## Contents

- [Lockable Answers](#lockable-answers)
- [Open-First Theme Answers](#open-first-theme-answers)
- [Invalid-Answer Loop](#invalid-answer-loop)
- [Answer Failure Types](#answer-failure-types)
- [Coverage And Closure Failures](#coverage-and-closure-failures)
- [Blocking Format](#blocking-format)

## Lockable Answers

A material decision is lockable when the answer resolves the exact leaf through
one or more of:

- an explicit choice or default;
- a measurable acceptance criterion;
- a bounded scope or named non-goal;
- a concrete constraint or owner;
- an acknowledged tradeoff or risk disposition;
- an evidence source or verification method;
- an explicit user-owned deferral.

An unambiguous `1`, `yes`, or “use the recommendation” is a complete answer to
the presented choice. Do not demand a rationale unless evidence conflicts with
the choice or the rationale itself controls another material branch. Lock only
that leaf and propagate its consequences.

A `blocking` open question is a valid state, not a lockable answer. Before
treating evidence as missing, inspect any scoped source, path, command, test,
metric, current behavior, or authoritative reference that can answer the fact
without user authority.

## Open-First Theme Answers

The first question for a new material theme is exploratory, not a presented
choice. Ask one neutral open-ended question and wait without a timeout. Do not
include a recommendation, default, option list, suggested wording, or an
auto-resolving prompt.

The answer is sufficient when it exposes the user's framing, desired behavior,
constraints, concerns, or values well enough to discover the theme's real
leaves. It need not lock every leaf. If it is too vague to identify the branch,
ask one narrower open follow-up before presenting choices. Once the theme is
framed, use recommendations or real alternatives for specific material leaves.

Silence and elapsed time are not invalid answers; they are no answer. Keep the
question pending until the user responds, explicitly defers, pauses, or stops.

## Invalid-Answer Loop

When an answer is not lockable:

1. State that the current leaf remains unresolved.
2. Name the exact failure below.
3. Re-ask the same decision more narrowly.
4. Give the minimum lockable answer. After the theme-opening answer, include a
   recommendation or real alternatives when they materially help.
5. Wait. Do not switch themes, implement, or hide the gap as an assumption.

## Answer Failure Types

### Vague Preference

Examples include “都可以”, “看情况”, “随便”, “先这样”, or “应该差不多”
when a default materially affects the outcome.

- Explain that no default behavior was selected.
- Ask for an explicit option, default, or deferral.
- Do not reject a short answer merely because it is short; reject ambiguity.

### Skipped Decision

The answer discusses background or motivation without resolving the requested
choice.

- Name the still-missing choice.
- Ask whether to select a concrete option or explicitly defer the leaf.

### Missing Acceptance Criterion

The user states a direction but not what observable result would prove success.

- Ask for the behavior, artifact, metric, comparison, or manual check that
  decides completion.
- Ensure the evidence can distinguish success from a plausible false pass.

### Missing Constraint Or Owner

The answer ignores a binding limit or leaves execution, approval, maintenance,
or recovery ownership unclear.

- Surface the specific unresolved constraint or role.
- Do not ask for generic priorities when only one concrete boundary matters.

### No Tradeoff

The answer attempts to maximize incompatible goals without selecting which one
governs conflict.

- State the actual incompatibility.
- Ask which outcome wins under the concrete conflict.

### No Evidence

The answer asserts a fact that drives scope, safety, correctness, risk, or
go/no-go without an observable source.

- First perform bounded investigation when the fact is discoverable.
- If authority or unavailable evidence is required, ask for the source or mark
  the leaf blocking.
- Do not treat a user preference, permission, or value judgment as a fact that
  should be discovered externally.

### Scope Drift

The answer adds adjacent goals, systems, or artifacts without defining which
parts enter the current delivery slice.

- State the newly introduced branch and consequence.
- Ask whether it is in scope, deferred, or a non-goal.

### Unverifiable Wording

Terms such as “better”, “stable”, “simple”, “complete”, or “not too complex” do
not identify an observable outcome.

- Ask what a reviewer, test, metric, or user would observe if the term were
  satisfied.

### Contradiction With Evidence

The answer conflicts with code, config, tests, docs, runtime evidence, inherited
constraints, or an earlier decision.

- State the exact conflict and source.
- Ask which authority should govern or whether more evidence is needed.
- Reopen only leaves whose closure depended on the contradicted premise.

### Unsupported Rationale Demand

The user selected a presented option clearly, but the interviewer keeps asking
why without a decision-relevant conflict.

- Lock the option.
- Do not manufacture a rationale requirement to prolong grilling.
- Open only consequences that materially follow from the choice.

## Coverage And Closure Failures

### Premature Closure Or Missing Branch

The current question was answered, but the surrounding theme, applicable pack,
or second-order consequence was never audited.

- Close only the answered leaf.
- Generate and classify the omitted branches before selecting the next question.
- `blocking == 0` is not closure until all three passes succeed.

### Dependency Not Propagated

A choice changes data, interface, compatibility, security, operations,
acceptance, or another downstream contract, but those leaves retain stale
statuses.

- Invalidate the affected statuses.
- Record the dependency edge and reopen material consequences.

### Unsupported Not Applicable

A dimension is marked `not-applicable` without evidence that it cannot affect
the delivery slice.

- Restore it to `open`.
- Record the exclusion reason and evidence before closing it again.

### Unsafe Assumption

A material, costly, irreversible, user-visible, security-sensitive, or
acceptance-changing decision was converted into an assumption.

- Restore it to `blocking`.
- Only non-material, low-risk, reversible details may use `assumption`.

### Unowned Deferral

Codex deferred a material decision without an explicit user choice.

- Restore it to `blocking`.
- Explain the consequence of deferral and ask the user to defer or resolve it.

### Implicit Risk Acceptance

A material downside is listed but has no `avoid`, `mitigate`, `accept`, or
`defer` disposition.

- Keep the gate closed.
- Ask for the disposition as one material decision.
- A mitigation must state the remaining risk; mitigation is not automatic
  acceptance.

### Option Anchoring

The interview accepts the user's proposed solution or the offered options
without testing the problem framing, smaller alternatives, hidden coupling, or
failure conditions.

- Reopen the relevant problem or approach leaf.
- If the theme never received a neutral open question, return it to `unopened`
  and ask that question before presenting another option set.
- Present a different option only when it is genuinely viable and changes the
  decision; do not invent alternatives for ceremony.

### Incomplete Evidence Provenance

A leaf is labeled locked but has no user decision, evidence, inherited
constraint, safe assumption, explicit deferral, or justified not-applicable
source.

- Add the exact source reference or reopen the leaf.
- Do not use the model's confidence as provenance.

### Failed Closure Pass

Coverage, consistency, or adversarial review finds a new material gap.

- Record the gap as a leaf.
- Resume the one-decision loop.
- Repeat only the closure evidence affected by the new answer.

### Missing Coverage Confirmation

The three passes succeeded but the user has not confirmed the complete ledger.

- Show the ledger and accepted residual limitations.
- Ask for explicit coverage confirmation.
- Preauthorized planning or implementation does not substitute for this gate.

## Blocking Format

Use this compact Chinese form when a leaf cannot proceed:

```markdown
阻断问题：<one material decision>
阻断原因：<missing decision, evidence, disposition, or contradiction>
最低所需答案：<choice, default, source, criterion, or explicit deferral>
推荐选项：<recommendation or none>
擅自假设的风险：<specific consequence>
受影响分支：<dependent leaves>
```

Omit `推荐选项` while opening a theme. This form never sets a timeout or
authorizes an automatic default.

If the user stops, preserve this blocker in the incomplete brief. Do not smooth
it over, call the requirements locked, or infer acceptance from silence.
