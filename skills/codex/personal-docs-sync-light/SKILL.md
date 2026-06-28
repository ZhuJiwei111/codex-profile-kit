---
name: personal-docs-sync-light
description: Use after code or config changes that may make developer docs, README, commands, APIs, environment setup, examples, or user-facing workflow descriptions stale.
---

# Personal Docs Sync Light

Update docs only when they would otherwise become false or misleading.

## Check

1. Identify behavior, config, command, API, environment, or workflow changes.
2. Search docs for changed names, commands, paths, env vars, and user-visible
   concepts.
3. Patch the smallest relevant doc text directly; do not write temporary
   Markdown generators for README or guide updates.
4. If statistics or scans are useful, generate structured evidence such as CSV,
   JSON, or text summaries, then integrate it into the docs manually.
5. Verify by reading the edited section and checking links or commands when cheap.

## Skip

- Internal refactors with no doc-visible effect.
- Formatting-only code changes.
- New tests that do not change documented behavior.
- Broad documentation rewrites unrelated to the task.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Updating docs because code changed somewhere | Update only stale or missing docs |
| Rewriting large pages | Patch the smallest false section |
| Generating final Markdown with a script | Use scripts for evidence, then write prose directly |
| Forgetting commands/env vars | Search exact literals before deciding no docs changed |
