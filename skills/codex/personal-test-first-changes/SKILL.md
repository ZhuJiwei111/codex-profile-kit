---
name: personal-test-first-changes
description: Use before implementing a bug fix, feature, refactor, or behavior change when a local test harness or cheap executable check exists.
---

# Personal Test First Changes

Prefer test-first evidence for behavior changes. Scale the ritual to risk and the
available harness.

## Default

- For bug fixes: reproduce the bug with a focused failing test or executable
  check before changing code.
- For new behavior: write or identify the smallest check that describes expected
  behavior, then implement the minimum passing change.
- For refactors: run a focused pre-check, refactor, then re-run the same check.

## Exceptions

Do not force TDD for docs-only edits, config-only edits, generated code,
throwaway prototypes, or projects with no usable harness. Use the smallest
reliable verification and report the gap.

## Red Flags

| Red flag | Response |
| --- | --- |
| Test passes before code change | It is not proving the new behavior |
| Only manual testing exists | Add an automated check if cheap |
| Test setup is huge | Narrow the case or report harness limitations |
