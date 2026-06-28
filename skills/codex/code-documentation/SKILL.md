---
name: code-documentation
description: Use when generating or improving standalone code documentation, architecture guides, code explanations, API docs, onboarding tutorials, or technical walkthroughs from an existing codebase.
metadata:
  sources:
    - https://github.com/wshobson/agents/tree/main/plugins/code-documentation
---

# Code Documentation

## Scope

This skill adapts the upstream `code-documentation` plugin into one Codex skill for documentation production. It covers three modes: explain code, generate reference/architecture docs, and build tutorials.

## Boundaries

Use these instead when appropriate:

- `docs-sync`: updating project docs after code changes.
- `receiving-code-review` or `requesting-code-review`: review findings and correctness risks.
- `code-simplifier`: simplifying code while preserving behavior.
- Project `AGENTS.md`: repository-specific documentation style.

## Mode Selection

| User Need | Mode | Output |
|---|---|---|
| "Explain this file/module" | Explain | Concise walkthrough with file references. |
| "Generate docs/manual/API docs" | Document | Structured Markdown documentation. |
| "Create onboarding/tutorial" | Tutorial | Step-by-step learning path with prerequisites and checks. |

## Documentation Workflow

1. Identify the target audience and artifact type from the user request.
2. Inspect only the relevant files first; expand search when structure is unclear.
3. Preserve repository terminology and established doc style.
4. Prefer concrete file links and verified behavior over broad claims.
5. Separate facts observed in code from inferences.

## Evidence And Markdown

- Write final Markdown docs, architecture guides, tutorials, and reports
  directly as human-readable Codex-authored prose.
- Use scripts only to extract evidence such as facts, counts, table data,
  source locations, or structured summaries.
- Do not generate Markdown prose with Python templates unless the user asks for
  it or the artifact is mostly mechanical.

## Architecture Guides

Include:

- System boundary and entry points.
- Major components and ownership.
- Data flow and state transitions.
- Key design decisions and tradeoffs.
- Operational concerns: configuration, tests, deployment, failure modes.

## Tutorials

Include:

- Prerequisites and expected final result.
- Small runnable steps.
- Frequent validation checkpoints.
- Common errors and recovery.
- Next steps for deeper work.

## Common Mistakes

| Mistake | Correction |
|---|---|
| Writing marketing prose | Write operational technical docs. |
| Guessing architecture | Mark inferences and verify with code. |
| Duplicating generated API output | Summarize and link to source where possible. |
| Mixing review with documentation | Use review skills for defects; use this skill for explanatory artifacts. |
