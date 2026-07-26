---
name: personal-test-first-changes
description: Use before implementing a bug fix, feature, behavior change, or behavior-preserving refactor when a focused test or cheap executable check is practical. Not for diagnosis-only work or final completion verification.
---

# Personal Test First Changes

Establish the smallest useful behavior evidence before changing implementation.
Choose the evidence semantically; do not create a named mode record or separate
role ceremony.

## Choose Proportionate Evidence

- For missing or incorrect behavior, add or identify a focused check that can
  demonstrate a valid RED before the implementation change.
- For a behavior-preserving refactor or cleanup, obtain a fresh passing baseline
  and rerun the same check after the change; do not manufacture a failure.
- When neither is practical, use the strongest cheap alternative, such as a
  parser, schema check, static check, build, dry run, targeted readback, or
  manual contract comparison, and report the gap.

Use the project's actual environment and narrowest relevant command. Resolve a
materially ambiguous behavior decision before writing the check. Preserve user
and prior-stage work rather than rolling it back merely to create historical
RED evidence.

## Validate RED

For a behavior change:

1. Test one observable contract or regression input.
2. Run the focused check before changing production behavior.
3. Accept RED only when the check runs, fails, and the failure signal matches
   the missing or incorrect target behavior.

A syntax error, import error, bad fixture, missing dependency, wrong command, or
unrelated baseline failure is not valid RED. Correct an obvious mistake in the
new check or command and rerun it. If the failure remains unexplained, flakes,
hangs, or repeats for a different reason, use personal-evidence-debugging.

If the check unexpectedly passes, determine whether the behavior already
exists, the reproduction is wrong, or the check is ineffective before changing
production code.

## Make The Smallest Coherent Change

Implement only the scoped behavior needed for the valid RED or preserving
contract. Do not weaken assertions, blindly refresh snapshots, or change
expected results to match an unexplained implementation.

Rerun the same focused check. Then run only the cheapest directly coupled checks
warranted by risk. Keep known unrelated baseline failures visible without
expanding scope to repair them.

Refactor only when it is in scope and the relevant checks remain green.

## Test Real Behavior

- Prefer public results and contracts over private structure.
- Mock expensive, external, or nondeterministic boundaries only after
  understanding the real side effects the subject relies on.
- Use interaction assertions as primary evidence only when the interaction is
  itself the contract.
- Do not add test-only production APIs or duplicate implementation logic inside
  tests.
- Keep a durable regression test when it naturally belongs in the project
  harness; otherwise identify the temporary or manual evidence limit.

Do not install dependencies or launch heavy or long-running checks merely to
satisfy test-first form. Use a cheap proxy or report the unavailable evidence
unless that separate action is authorized.

## Report

Report the focused command or check, the before-change result and expected
reason, the after-change result, directly coupled checks, and any evidence gap.
This is implementation evidence, not the final task verdict.

Read references/source-notes.md only when maintaining this skill.
