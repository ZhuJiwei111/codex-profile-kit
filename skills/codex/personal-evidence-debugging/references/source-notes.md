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
