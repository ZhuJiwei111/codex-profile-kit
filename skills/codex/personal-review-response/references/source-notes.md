# Source Notes

## Local Artifact

- Skill: `personal-review-response`
- Review date: 2026-07-11
- Local purpose: evaluate review feedback, assign a technical disposition, and
  route only authorized accepted work while keeping external review state
  separate.

## Pinned Upstream Source

- Project: [obra/superpowers](https://github.com/obra/superpowers)
- Release: [v6.1.1](https://github.com/obra/superpowers/releases/tag/v6.1.1)
- Annotated tag object: `c984ea2e7aeffdcc865784fd6c5e3ab75da0209a`
- Peeled release commit: `d884ae04edebef577e82ff7c4e143debd0bbec99`
- Source file: [`skills/receiving-code-review/SKILL.md`](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/receiving-code-review/SKILL.md)
- Source blob: `4c77a10ee338fb7bddec6f5acf3455c8f2e4465a`
- License: [MIT](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/LICENSE),
  Copyright (c) 2025 Jesse Vincent
- Upstream checked: 2026-07-11

The pinned release is design evidence, not a runtime dependency. No upstream
scripts or operational references are required by this local skill.

## Adopted

- Read feedback in context before acting.
- Treat review statements as technical claims that require verification.
- Separate the underlying concern from the reviewer's proposed implementation.
- Ask for clarification when missing information changes the technical
  decision.
- Push back with concrete technical evidence when a claim is wrong or risky.
- Check real usage and current requirements before accepting speculative scope.
- Process related feedback with attention to dependency and verification.
- Avoid performative agreement that substitutes for technical reasoning.

## Adapted For This Profile

- Added explicit `accepted`, `rejected`, and `needs-clarification`
  dispositions.
- Separated disposition, local implementation authority, verification, reply,
  and thread state.
- Limited ambiguity blocking to the affected dependency cluster instead of
  stopping every independent item.
- Replaced fixed simple-to-complex ordering with dependency, shared-root-cause,
  risk, safety, and verification-isolation ordering.
- Expanded YAGNI checks beyond direct call sites to public and dynamic
  contracts.
- Added stale head, CI provenance, batch deduplication, and shared-fix mapping.
- Routed accepted behavior changes, unknown failures, documentation drift,
  final verification, and Git readiness to their owning personal skills.

## Rejected Or Deliberately Omitted

- No identity-based assumption that a trusted person is technically correct or
  that an external reviewer is inherently unreliable.
- No automatic implementation after understanding a comment.
- No global stop because one independent comment is ambiguous.
- No inference that missing direct call sites prove code is unused.
- No absolute ban on thanks or ordinary professional courtesy.
- No copied GitHub API reply command or built-in external mutation path.
- No automatic refactor, compatibility removal, dependency installation, CI
  rerun, reply, thread resolution, commit, push, or PR state change.

## Local Boundaries

- `personal-review-response` owns claim extraction, evidence review,
  disposition, comment dependency mapping, and review-state accounting.
- `personal-test-first-changes` owns the RED/GREEN loop for authorized accepted
  behavior changes.
- `personal-evidence-debugging` owns unknown failure and root-cause
  investigation.
- `personal-brainstorms` owns consequential design work opened by feedback.
- `personal-docs-sync-light` owns identified documentation contract drift.
- `personal-risk-verification` is the single final completion gate.
- `personal-branch-finish` owns later Git readiness and handoff decisions.

Reviewer text and platform state are external evidence. They do not broaden
local authorization or confer permission for external writes.
