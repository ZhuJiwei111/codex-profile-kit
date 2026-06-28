---
name: personal-risk-verification
description: Use before reporting local code, config, docs, or repository changes as complete, especially after edits that affect behavior, commands, APIs, tests, builds, packaging, or user-visible workflows.
---

# Personal Risk Verification

Completion claims need evidence. Match verification to the blast radius.

## Choose Checks

| Change | Preferred verification |
| --- | --- |
| Behavior or bug fix | Focused test, then nearby suite if cheap |
| Shared API, schema, types | Typecheck, contract test, import check, or parser check |
| CLI, scripts, config | Dry run, `--help`, syntax validation, or minimal smoke command |
| Docs-only | Edited-section readback, literal command/path consistency check |
| No runnable harness | Diff inspection plus explicit residual risk |

## Rules

- Run the narrowest meaningful command first.
- Broaden for shared or user-facing surfaces.
- Do not claim “passes” from memory or unrelated runs.
- If skipped, say why: missing dependency, unclear env, long job, approval needed,
  or no local harness.
