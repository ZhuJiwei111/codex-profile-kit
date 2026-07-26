---
name: personal-code-simplifier
description: Manual only. Use only when the user explicitly invokes this skill for a bounded behavior-preserving simplification of named code, or explicitly includes that cleanup as a scoped workflow step; not for unsolicited cleanup, behavior changes, diagnosis, or repository-wide refactoring.
---

# Personal Code Simplifier

Make the named code easier to understand while preserving observable and
contract-relevant behavior. Clarity and lower total complexity matter; fewer
lines do not by themselves.

## Bound The Change

Identify the exact files or symbols, protected behavior, independently owned
changes, and the local complexity being removed. For one obvious hunk this may
remain implicit. Stop if the target cannot be separated safely from unrelated
work or a design decision.

Run the narrowest practical existing check before editing. Use the same check
afterward; if no harness exists, use the strongest cheap parser, type, build, or
contract comparison and state the gap.

## Simplify Locally

- Reduce unnecessary nesting, indirection, duplication, or cleverness while
  preserving evaluation, exception, ordering, and side-effect behavior.
- Consolidate only paths that actually share invariants.
- Prefer existing patterns and dependencies. Do not add a framework,
  compatibility layer, configuration surface, or speculative abstraction.
- Do not infer dead code from one missing call site; consider public,
  registration, reflection, generated, plugin, and compatibility surfaces that
  are relevant to the target.
- Avoid unrelated formatting, public API changes, and architecture changes
  disguised as cleanup.

Inspect the final scoped diff and report the material simplification, the
before-and-after evidence, and any remaining equivalence gap.

Read `references/source-notes.md` only when maintaining provenance.
