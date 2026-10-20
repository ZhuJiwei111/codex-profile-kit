---
name: code-review
description: Review a requested diff, branch, PR, or working-tree change for correctness, requirement gaps, and material violations of repository standards.
---

# Code Review

Review the requested surface without editing it. Resolve its actual comparison
base, staged/unstaged state, or PR scope before drawing conclusions; do not
silently omit uncommitted work or assume a local main branch is current.

Inspect the affected flow and relevant callers, tests, repository standards,
and originating user request, issue, or specification. A missing issue-tracker
configuration is not a reason to install a workflow or block an ordinary review.
Use the user's request as the requirement source when no formal spec exists;
disclose a material gap instead of inventing requirements.

Consider two perspectives:

- Requirements: missing behavior, incorrect behavior, scope expansion, and
  realistic regressions at the affected boundary.
- Standards: material documented contract violations and design problems with
  a concrete consequence. A stylistic preference or named code smell alone is
  not an actionable finding.

For a small change, inspect both directly. Use independent bounded reviewers
only when delegation is authorized and their independence can improve the
review; the parent owns synthesis. Run a focused existing check when it can
distinguish a real concern, not to fill a fixed validation stack.

Return actionable findings ordered by consequence, with a tight code location,
triggering scenario, and evidence or requirement. Identify the perspective when
useful; combine duplicate findings. If none remain, say so and state only a
material verification gap. Do not stage, commit, publish, or fix merely because
the review completed.
