---
name: personal-code-simplifier
description: Use only for an explicit bounded behavior-preserving code simplification request or an authorized workflow's clearly scoped cleanup step. Not for unsolicited cleanup, behavior changes, diagnosis, review decisions, or repository-wide refactoring without a bounded scope.
---

# Personal Code Simplifier

Make bounded code easier to understand and maintain while preserving its
observable and contract-relevant behavior. Clarity, not line-count reduction, is
the goal.

## Establish The Boundary

Use any concise format that makes these facts clear:

- target: the exact files, symbols, or hunks to simplify;
- protected behavior: outputs, errors, side effects, ordering, interfaces,
  compatibility, and other relevant contracts;
- protected changes: user or independently owned work that must remain intact;
- intended changes: the local complexity, duplication, nesting, or cleverness
  being removed; and
- stop condition: uncertainty or overlap that would turn cleanup into a
  behavior or design change.

Keep the boundary implicit for one obvious function or hunk. Do not absorb a
whole dirty file or repository merely because part of it is in scope. If target
and protected work cannot be separated safely, stop and ask.

## Establish Preserving Evidence

Before editing, run the narrowest meaningful existing test or cheap executable
check and require a fresh passing baseline for the target behavior. When no
usable harness exists, use the strongest proportionate alternative, such as a
parser, static or type check, build, direct contract comparison, or focused
readback, and state the gap.

After each coherent layer when warranted, and always after the final change,
rerun the same core check plus the cheapest directly coupled checks. An
unexpected or unexplained failure leaves this workflow and enters
personal-evidence-debugging; do not stack speculative fixes into cleanup.

## Simplify Locally

Prefer transformations with a local behavior argument:

- reduce nesting while preserving evaluation, exception, and side-effect order;
- replace clever expressions with explicit control flow;
- consolidate duplication only when the paths share the same invariants;
- rename private locals or helpers only after checking relevant dynamic,
  serialization, reflection, and external-use surfaces;
- remove redundant branches only when reachability and consumers are understood;
  and
- remove comments that merely restate code while preserving rationale,
  constraints, directives, generated inputs, and licenses.

Avoid dense one-liners, speculative abstractions, new dependencies, new
configuration, public API changes, unrelated formatting, and architecture
changes disguised as cleanup.

Do not infer dead code from the absence of a direct call site. Check public and
compatibility surfaces, registration, reflection, plugins, generated ownership,
and external consumers. If those facts remain unknown, keep the code or narrow
the edit.

## Review And Report

Inspect the final scoped diff and confirm:

- every changed hunk belongs to the cleanup target;
- protected changes remain intact;
- behavior, exceptions, ordering, side effects, and public surfaces did not
  drift within the evidence boundary; and
- each transformation creates a concrete clarity or maintainability gain.

Report the target, material simplifications, before-and-after checks, remaining
equivalence gap, and anything deliberately left unchanged. Final task
completion remains with personal-risk-verification.

Read references/source-notes.md only when maintaining this skill.
