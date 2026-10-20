# Source Notes

Checked: 2026-07-18.

## Upstream Design Source

- Project: Superpowers systematic-debugging
- Release: v6.1.1
- Commit: d884ae04edebef577e82ff7c4e143debd0bbec99
- Source:
  https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/systematic-debugging/SKILL.md
- License: MIT, Copyright 2025 Jesse Vincent.

The local workflow independently rewrites the source ideas and bundles none of
its scripts or project-specific examples.

## Local Preferences

- Use a short deterministic fast path before advanced investigation.
- Lock expected versus observed behavior, reproduce narrowly, identify the first
  causal failure, and test one hypothesis with a prediction and falsifier.
- Label conclusions confirmed, likely, or unknown.
- Repeated failed fixes require a materially different causal model, but no
  fixed attempt count.
- Keep expected RED with test-first work and final completion with final
  verification.

## 2026-10-20 review

Reviewed the current upstream entry at `obra/superpowers@bb92a77741419a4ab5f06e711a283343f1ada0c3`.
It still prescribes sequential phases, test-first repair, and an architecture
question after three failed fixes. These are not imported: the current portable
contract favors a direct evidence fast path, proportionate checks, and changing
the causal model instead of counting attempts. Retain the local rewrite.

Community issue https://github.com/obra/superpowers/issues/1120 reports review
overhead on mechanical tasks. It concerns another Superpowers workflow and is
context for avoiding universal orchestration, not proof this debug skill fails.
