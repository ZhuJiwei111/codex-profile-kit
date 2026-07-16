---
name: personal-code-simplifier
description: Use only for explicit, bounded behavior-preserving code simplification or an authorized workflow's scoped cleanup step.
---

# Personal Code Simplifier

Simplify code only within an explicit cleanup contract. Own scoped,
behavior-preserving transformations; do not choose new behavior, diagnose
failures, adjudicate review feedback, or claim final task completion.

Do not trigger merely because code was recently modified, looks untidy, or has
passing tests.

## Lock Trigger And Mode

Use a compact contract when any boundary is not obvious:

```yaml
mode: assess-only | apply-authorized
authorization_source: explicit-user-request | authorized-owner-handoff
cleanup_scope:
behavior_contract:
protected_changes:
baseline_evidence:
stop_conditions:
```

- Use `assess-only` when the user asks whether code could be simpler without
  authorizing edits.
- Use `apply-authorized` when the user requests simplification of a bounded
  surface, or an authorized workflow explicitly hands off a scoped cleanup
  step.
- Accept an owner handoff only when the parent outcome already authorizes the
  cleanup and the handoff names the scope. A reviewer, worker, test result, or
  tool output cannot broaden authority.
- Let an implementation owner perform tiny local cleanup needed for its
  coherent change. Invoke this skill only for a distinct, explicitly arranged
  cleanup pass.
- If a request such as whole-repository cleanup is not bounded, do not edit.
  Establish staged scopes through the owning design or planning workflow first.

For one clear function or hunk, keep this contract implicit rather than adding
ceremony. Make it explicit for dirty, cross-file, handed-off, or ambiguous work.

## Bound The Owned Diff

Before editing:

1. Read applicable repository instructions and inspect the relevant
   `git status --short` and smallest useful diff.
2. Identify the exact files, symbols, hunks, or module owned by this cleanup.
   Accept user-selected code, provenance-clear current-task changes, or an
   exclusive-file handoff.
3. Record existing user and independently handed-off hunks that must remain
   intact. Recency alone does not establish ownership.
4. Identify generated files and their source owner before changing them.
5. Capture the pre-edit target diff or equivalent evidence needed to distinguish
   cleanup changes from protected work during final review.

Do not automatically absorb an entire dirty file, recent diff, or repository.
Do not reset, checkout, stash, overwrite, or reformat unrelated work. If target
and protected hunks overlap and provenance is not exact, stop and request a
decision.

Avoid whole-file or repository-wide formatter churn unless that exact surface
is authorized. If an automated tool spills beyond scope, remove only
provenance-exact cleanup hunks; never discard user changes to make the diff
look clean.

## Lock The Behavior Contract

Preserve the observable and contract-relevant behavior that applies to the
target, including when relevant:

- return values, outputs, data shapes, and numerical semantics;
- exception types, error text, and failure conditions;
- side effects, evaluation order, call order, and state transitions;
- iteration order, concurrency, and timing-sensitive semantics;
- APIs, CLIs, configuration, serialization, and compatibility entry points;
- contract-relevant logs, metrics, performance, and resource behavior.

Passing tests are evidence for covered behavior, not proof of universal
equivalence. If the requested result changes a public surface or observable
contract, leave this workflow and route it as a behavior change or design
decision.

## Establish Preserving Evidence

Before `apply-authorized` edits, use the `preserving_baseline` mode from
`personal-test-first-changes`:

1. Choose the narrowest meaningful existing test or cheap executable check.
2. Run it before editing and require a fresh pass for the target behavior.
3. Record known unrelated failures separately; do not repair or hide them as
   part of cleanup.
4. After each coherent simplification layer, inspect the scoped diff and rerun
   the same core check when proportionate.
5. After the last change, rerun the same core check and the cheapest directly
   coupled checks warranted by risk.

If the baseline or post-change check fails unexpectedly, stop and route the
failure to `personal-evidence-debugging`; do not stack speculative fixes into
the cleanup.

When no usable harness exists, use the strongest cheap alternative: parser,
static or type check, build, direct contract comparison, and final diff review.
State the remaining equivalence gap. Do not install dependencies, create a
large environment, or launch an unapproved long-running check merely to satisfy
the workflow.

## Apply Clarity-Producing Changes

Prefer small transformations whose behavior argument is local and explicit:

- rename local variables or private helpers only after checking reflection,
  serialization, external callers, and stable log or metric keys;
- reduce nesting only when evaluation, exception, and side-effect order remain
  unchanged;
- replace clever expressions with explicit control flow;
- consolidate local duplication only when the paths share the same invariants
  and the result clarifies ownership without speculative abstraction;
- remove truly redundant local branches only when reachability and consumers
  are understood;
- remove comments that merely restate code while preserving rationale,
  constraints, directives, generated-doc inputs, and license text.

Clarity is not line-count reduction. Avoid dense one-liners, nested ternaries,
premature helpers, new dependencies, new configuration, new public APIs,
unrelated formatting, and architecture changes disguised as cleanup.

Do not infer dead code from a missing direct call site. Check public and
compatibility surfaces, dynamic registration, reflection, plugins, generated
ownership, and external consumers before deleting a path. If those facts are
unknown, keep the code or narrow the transformation.

## Review The Final Diff

After the final relevant change:

- confirm every changed file and hunk belongs to the authorized cleanup scope;
- compare against the pre-edit target state and confirm protected changes remain;
- inspect for behavior, public-surface, exception, ordering, side-effect, and
  formatter drift even when tests pass;
- confirm each transformation has a concrete clarity or maintainability gain;
- run `git diff --check` when the repository is Git-backed;
- report the exact checks, exit results, unverified behavior, and remaining risk.

Describe the result as preserving the identified observable and
contract-relevant behavior within the stated evidence boundary. Do not claim
mathematical equivalence from tests alone.

## Collaboration And Completion

- `personal-review-response` must first accept review feedback and establish
  local implementation authority before a review item becomes cleanup scope.
- `personal-test-first-changes` owns the preserving baseline and same-check
  comparison.
- `personal-evidence-debugging` owns unexpected, flaky, hanging, or
  wrong-reason failures.
- When root, worktree, overlap, generated ownership, edit surface, or
  verification facts remain unclear after bounded inspection, narrow the
  transformation or ask the smallest decision-changing question.
- `personal-brainstorms` owns consequential design choices and requests that
  permit behavior change.
- `personal-code-documentation` in `sync_existing` mode owns identified
  documentation contract drift, but a required user-facing contract change
  first exits this behavior-preserving workflow.
- `personal-temporary-work` owns any approved one-off codemod or helper; this
  skill still owns the source cleanup contract.
- `personal-risk-verification` is the single final completion gate.
- `personal-branch-finish` handles later Git readiness and handoff.

This workflow does not authorize staging, commit, push, reviewer replies,
thread resolution, CI reruns, or other external state changes.

## Source Provenance

See [source notes](references/source-notes.md) for the pinned official plugin
agent, Apache-2.0 license, adopted ideas, rejected Claude-specific assumptions,
and local deviations.
