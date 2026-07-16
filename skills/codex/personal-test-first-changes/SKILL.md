---
name: personal-test-first-changes
description: Use before implementing a bug fix, feature, behavior change, or refactor when a focused test or cheap check is practical.
---

# Personal Test First Changes

Establish local evidence before changing behavior. Scale the cycle to the
available harness, risk, and authorization boundary.

The main process locks the behavior, authority, and acceptance boundary. A
bounded executor owns substantive RED/GREEN commands and edits, then returns
raw command, revision, exit-status, and scope evidence for intake. That evidence
supports later verification but is not a task-level verdict.

## Choose The Evidence Mode

Choose one mode before changing task-owned behavior:

- `red_green`: use for a bug fix, feature, runtime behavior change, or
  generator behavior change when a focused test or cheap executable check is
  practical.
- `preserving_baseline`: use for a behavior-preserving refactor or explicitly
  scheduled bounded cleanup. Obtain a passing pre-change baseline; do not
  manufacture a failing test.
- `alternate`: use for a non-behavior change, or when neither a valid RED nor a
  fresh preserving baseline is proportionately available. Record the substitute
  evidence and remaining gap.

Do not use this workflow for diagnosis-only work or final completion
verification. Route those phases to their dedicated owners.

## Preflight

1. State the observable behavior boundary and expected result.
2. Confirm the edit owner, focused check, `cwd`, environment owner, expected
   runtime, and material side effects. If one of those repository facts remains
   unclear after bounded inspection, stop and ask the smallest question that
   changes the RED/GREEN boundary.
3. If the required behavior is still ambiguous, resolve it through discussion,
   `personal-brainstorms`, or the owning plan before writing a test.
4. Preserve existing user and independently handed-off prior-stage work. Do not
   revert or delete it merely to manufacture RED. Handle a separately explicit
   destructive request through the normal exact-scope, authorization, and
   recovery boundaries.
5. A current-task Codex edit made before the check may be safely withdrawn
   within existing implementation authority only when its provenance and
   non-overlap are exact. Otherwise treat it as user work and report missing
   RED evidence.

Keep a compact conversational record; do not create a state file for this
workflow:

```yaml
evidence_mode:
behavior_boundary:
focused_check:
pre_change_result:
expected_failure_reason:
implementation_scope:
post_change_result:
nearby_checks:
evidence_gap:
```

## RED: Prove The Check Fails Correctly

For `red_green` mode:

1. Write or identify the smallest focused check for one observable behavior.
   Prefer a public contract, boundary condition, or exact regression input.
2. Run the exact focused command before changing production behavior.
3. Accept RED only when all of these are true:
   - the check fails rather than merely failing to run;
   - the observed failure signal matches the expected one;
   - the failure is caused by the missing or incorrect target behavior, not a
     syntax error, import error, bad fixture, missing dependency, wrong command,
     or unrelated baseline failure.
4. If the check passes, stop. Determine whether the behavior already exists,
   the reproduction is wrong, or the check is ineffective. Do not claim RED or
   change production code on that evidence.
5. Correct an obvious mistake in the new check and rerun it without changing
   production behavior. Route an unexplained, flaky, hanging, or repeated
   wrong-reason failure to `personal-evidence-debugging`.

Keep a durable regression test when it naturally belongs in the project's
harness. If only a temporary executable check is proportionate, report that
limit explicitly.

## GREEN: Make The Smallest Coherent Change

1. Implement only the scoped behavior needed to satisfy the valid RED. Prefer
   the smallest coherent change over the fewest possible lines.
2. Do not weaken assertions, blindly refresh snapshots, or rewrite expected
   results to match an unexplained implementation.
3. Rerun the same focused command that produced RED and confirm the expected
   behavior now passes without new errors or warnings relevant to the change.
4. Run the cheapest directly coupled nearby checks when practical. Do not run
   the whole suite merely to satisfy the ritual.
5. Separate related regressions from known unrelated baseline failures. Do not
   hide the latter or expand scope to repair them without authorization.
6. Route unexpected GREEN failures to `personal-evidence-debugging` rather than
   stacking speculative fixes.

## REFACTOR: Stay Green

- Perform cleanup after GREEN only when it is in scope. Add no new behavior and
  rerun the focused and directly coupled checks after the cleanup.
- For a task whose purpose is a behavior-preserving refactor, first obtain a
  fresh passing baseline, change incrementally, and rerun the same evidence.
  A pre-change pass is required evidence in this mode, not a red flag.
- If the relevant baseline already fails, resolve or classify that failure
  before refactoring. Preserve unrelated baseline failures as explicit context.

## Test Real Behavior

- Prefer observable results and contracts over private structure.
- Mock only an expensive, external, nondeterministic, or out-of-scope boundary.
- Before mocking, identify the dependency's real side effects and the behavior
  used by the subject. Preserve those effects or move the mock boundary outward
  when they are part of the contract.
- Use interaction assertions as primary evidence only when the interaction is
  itself the contract.
- Do not add test-only production APIs, duplicate implementation logic inside
  tests, or approve an unexplained snapshot change.

## Risk-Scaled Alternatives

| Change | Minimum proportionate evidence |
| --- | --- |
| Docs-only | Edited-section readback and command, path, or link consistency |
| Formatting, metadata, or non-behavior config | Parser, schema, syntax, or targeted readback |
| Runtime behavior config | RED/GREEN with a parser, dry run, or focused behavior check when practical |
| Mechanical generated-output refresh | Verify source and generator ownership, then inspect the generated result; do not invent RED |
| Generator or generated-contract behavior | RED/GREEN at the generator contract or consumer boundary when practical |
| Explicit throwaway prototype | Minimal smoke evidence; add behavior tests before the work becomes durable product code |
| No usable harness | Try a cheap executable proxy; otherwise use static, diff, or manual evidence and report the gap |

When implementation already exists, distinguish provenance:

- For user or independently handed-off prior-stage work, add the strongest safe
  regression check and mark that RED was not observed. Roll it back only under
  a separately explicit, exact, recoverable authorization.
- For an exact, non-overlapping Codex edit made in the current authorized task,
  safely withdraw it when that restores a real pre-change boundary, then
  establish RED.
- When provenance or overlap is unclear, treat the implementation as user work
  and preserve the evidence gap.

## Authorization And Stop Conditions

- Treat cheap, focused local checks as normal implementation verification.
- Do not install dependencies, create a large environment, download assets,
  use heavy GPU resources, or launch a test expected to exceed 10 minutes only
  to satisfy test-first form. Obtain the required authorization first.
- If the only credible check is heavy or long-running, offer a cheap proxy or
  state its command, environment, resources, expected duration, and success
  signal before requesting launch approval. Do not start active monitoring by
  default.
- If the user declines tests, respect that boundary, use only permitted
  alternatives, and report that a test-first cycle was not completed.
- Stop when a behavior decision, environment choice, or scope expansion would
  materially change the implementation. Ask one decision-changing question.

## Collaboration And Completion Boundary

- Uncertain harness and ownership facts stop at bounded inspection and a
  decision-changing question before any check or edit.
- `personal-review-response` decides whether review feedback is accepted before
  an accepted behavior change enters this workflow.
- `personal-evidence-debugging` owns unexpected, flaky, hanging, or
  wrong-reason failures.
- `personal-code-documentation` in `sync_existing` mode updates an identified
  documentation contract after behavior or configuration changes.
- `personal-risk-verification` owns the only final completion gate and requires
  fresh evidence after the last relevant change.
- `personal-branch-finish` consumes completed verification evidence for Git
  readiness and handoff.

See [source notes](references/source-notes.md) for upstream evidence, adopted
principles, rejected dogma, and local deviations.
