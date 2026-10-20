---
name: personal-code-simplifier
description: Manual only. Simplify named code or an explicitly scoped cleanup while preserving behavior; exclude unsolicited cleanup and behavior changes.
---

# Personal Code Simplifier

Improve clarity and maintainability within the named surface. Optimize total
complexity rather than line count.

- Resolve the target files or symbols and preserve independently owned work.
  If scope comes from a diff, verify its actual base and changed paths; do not
  assume a local main branch is current or expand to its unrelated divergence.
- Use the narrowest practical existing baseline before and after a nontrivial
  refactor. If a meaningful check is unavailable, say so; visual inspection is
  not proof of behavior preservation.
- Remove needless nesting, indirection, and duplication only where the paths
  share real invariants. Prefer established patterns and installed dependencies.
- Preserve public contracts, side-effect order, exception behavior, numerical
  behavior, and literal content. Prompts, templates, configuration, and user
  strings are behavior: do not reword them as incidental code cleanup.
- Check registration, reflection, and public callers before declaring code dead.
  Avoid unrelated formatting and new abstractions without a present consumer.

If simplification requires changing behavior or an architectural decision,
separate that finding from the authorized refactor. Report the material change,
the before-and-after check, and any remaining equivalence gap.

Read `references/source-notes.md` only when maintaining provenance.
