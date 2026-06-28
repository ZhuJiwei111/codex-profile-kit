---
name: personal-review-response
description: Use when addressing code review, PR comments, requested changes, CI review notes, or inline feedback that may be unclear, questionable, or require implementation.
---

# Personal Review Response

Treat review feedback as a technical claim, not an order to blindly apply.

## Process

1. Read the comment in context and identify the exact requested change.
2. Verify whether the claim is correct against code, tests, docs, or behavior.
3. If correct, make the smallest coherent fix.
4. If incorrect or risky, explain the technical reason and propose a safer
   alternative.
5. Run focused verification and report any skipped checks.

## Guardrails

- Do not bundle unrelated refactors with review fixes.
- Preserve user changes and dirty worktree state.
- Prefer resolving the underlying issue over satisfying wording literally.
- For GitHub PR work, inspect unresolved threads before editing when thread
  state matters.
