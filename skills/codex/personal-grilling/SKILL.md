---
name: personal-grilling
description: Manual only. Use $personal-grilling for a multi-round, recommendation-first interrogation that resolves one material decision at a time, covers the semantic core plus applicable task packs, runs without timeouts, and ends only after three closure passes and explicit user confirmation.
---

# Personal Grilling

Pressure-test requirements before consequential planning or implementation.
Run only after explicit invocation and keep implicit invocation disabled.

## Lock A Scope Envelope

Before the first question, state a concise scope envelope:

- the decision or outcome being grilled;
- included and excluded work;
- fixed constraints and already locked decisions;
- decision owners and the current evidence cutoff;
- the acceptance boundary; and
- the action boundary while grilling is active.

Treat the proposed solution as a hypothesis. Test whether the problem is real,
whether a smaller approach works, what it couples to, and how it can fail. Do
not edit, launch, or implement while the gate is active. Perform only bounded
read-only investigation that can change a decision.

## Build Semantic Coverage

Read [coverage-model.md](references/coverage-model.md) before questioning. Cover
the universal core and add only applicable task packs. Derive further branches
from evidence, dependencies, user answers, and risks; the reference is a
discovery aid, not a fixed questionnaire.

Close each branch with observed evidence, a locked user decision, a safe
non-material assumption, an explicit deferral, or a justified not-applicable
finding. Keep the source, consequence, dependencies, and material risk visible.
Investigate discoverable facts instead of asking the user to supply them.

## Run The Multi-Round Decision Loop

1. Select the unresolved material decision with the highest safety,
   dependency, or rework impact.
2. If the real options are known, recommend one first and present no more than
   two alternatives with their material tradeoffs. Ask the user to choose,
   revise, defer, or reject them.
3. Use an open-ended question only when the option space is genuinely unknown.
   Explain why the answer matters and ask the smallest question that reveals
   that space; do not disguise a known menu as an open interview.
4. Ask exactly one material decision per user turn. A concise `1`, `yes`, or
   “use the recommendation” locks the presented decision without requiring an
   invented rationale.
5. Wait without a timer or automatic default. Silence, elapsed time, UI expiry,
   or tool behavior never answers, defers, pauses, or confirms a question.
6. After the answer, update the ledger, propagate consequences through scope,
   dependencies, risks, and acceptance, and identify the next highest-impact
   unresolved decision.

Continue across as many rounds as material coverage requires. Do not bundle
several decisions into a final questionnaire. Reopen only branches affected by
new evidence or a conflicting later decision.

## Control Assumptions And Risks

- Assume only details that are non-material, low-risk, reversible, and unable
  to change acceptance.
- Defer a material branch only through an explicit user choice.
- Mark not-applicable only when evidence shows that the branch cannot affect
  this scope.
- Give every material residual risk an explicit disposition: avoid, mitigate,
  accept, or defer. Naming a risk does not accept it.

## Close In Three Passes

After the last apparent decision, run these passes in order:

1. **Coverage:** account for the semantic core, applicable packs, derived
   branches, dependencies, and material risks.
2. **Consistency:** check that decisions, evidence, scope, constraints,
   interfaces, and acceptance agree and that late answers propagated.
3. **Adversarial:** challenge necessity, failure and recovery, abuse and
   security, compatibility and migration, operations and ownership, rollback,
   second-order effects, and whether acceptance can prove the outcome.

Resume the decision loop if any pass exposes a material gap.

When all three passes succeed, show a complete but proportionate ledger. Group
evidence-backed non-material or not-applicable items, but retain every material
decision, assumption, deferral, risk disposition, unresolved limitation, and
source boundary. Ask the user to explicitly confirm that coverage is complete,
then wait without a timeout.

## Stop Or Hand Off

Confirmation closes requirements coverage; it does not create implementation
authority. Preserve any same-scope authority already present in the original
request.

- If the user stops early, return an incomplete ledger and the exact open
  branches.
- If paired with `personal-brainstorms`, return the confirmed ledger for its
  sole design synthesis.
- If run alone, return the confirmed requirements ledger. Do not claim a design
  or implementation plan unless another authorized workflow owns it.

Use Chinese by default.

## Resources

- [coverage-model.md](references/coverage-model.md): compact semantic core,
  optional task packs, ordering, and closure guidance.
- [source-notes.md](references/source-notes.md): provenance and local
  preferences.
