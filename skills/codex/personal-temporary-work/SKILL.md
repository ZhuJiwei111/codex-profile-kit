---
name: personal-temporary-work
description: Use when doing one-off checks, statistics, temporary scripts, artifact post-processing, migrations, shard merging/splitting, local audits, or other work that should not become durable project code.
---

# Personal Temporary Work

Keep temporary work traceable and out of production paths.

## Decide

- If the task is a one-off check, statistic, migration, artifact rewrite,
  post-processing step, or local audit, prefer a helper script in `tmp/` over
  adding project-level branches, flags, or special-case logic.
- If future users or normal workflows need the behavior, update production code
  cleanly and use a temporary script only for existing artifacts or one-time
  cleanup.
- Compare direct transformation against regeneration. Prefer direct
  transformation when it is cheaper, preserves semantics, and can be verified.
- For documentation or report tasks, use temporary scripts to produce evidence
  files such as `.json`, `.csv`, `.tsv`, or `.txt` summaries; write final
  human-readable Markdown directly unless the user asks for generated reports.

## Location

- Put helper code under the relevant working directory's `tmp/` folder.
- In a repo, use the repo root `tmp/` unless a narrower artifact directory is
  clearly more appropriate.
- Outside a repo, use the current task directory's `tmp/`.
- Do not remove temporary helper code by default; preserve it for traceability.
- Do not commit `tmp/` helpers unless the user explicitly asks.

## Verification

- Add lightweight checks suited to the task: counts, ranges, schemas, checksums,
  sampled reads, before/after summaries, or dry runs.
- Report the helper path, command, input/output paths, evidence file paths, any
  final document path, and verification result.
- If temporary work touches large artifacts, long jobs, credentials, or heavy
  resources, follow the server-level Ask First rules.
