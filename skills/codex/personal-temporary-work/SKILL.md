---
name: personal-temporary-work
description: Use when one-off migration, conversion, repair, inspection, or artifact work might otherwise add permanent code. Separate durable behavior from temporary transition work and manage only the exact task-created scratch lifecycle.
---

# Personal Temporary Work

Keep one-off transition logic out of maintained code without turning temporary
file handling into a separate project.

## Choose The Surface

- durable: future normal users, environments, releases, or supported operations
  need the behavior. Implement it through the normal project owner.
- temporary: only bounded existing data, artifacts, or local state need one-time
  treatment. Use a temporary helper or direct command.
- hybrid: make the smallest durable change for future behavior and use a
  temporary helper for historical state.

Skip this skill for a direct command that creates no helper or retained
artifact. Do not call normal product behavior temporary to avoid its tests,
documentation, or maintenance owner.

## Place Temporary Work

Use the project's established scratch convention when one exists. Otherwise use
a safe task-specific temporary directory for disposable work.

Use a project- or worktree-local scratch directory only when recovery,
reattachment, audit, or handoff requires a stable path. Keep each worker's
scratch in its own owned surface. Do not automatically add or change
.gitignore, scanner configuration, or package inputs merely to hide temporary
work.

Keep formal deliverables at their requested output paths. A deliverable is not
temporary merely because a temporary helper produced it.

## Protect Inputs And Outputs

- Treat canonical inputs as immutable and write a new output by default.
- Define the actual properties that must be preserved, such as records, keys,
  order, schema, metadata, or higher-level semantics.
- Use staging, a sample, dry run, manifest, or output-adjacent temporary path
  only when it materially reduces transformation or recovery risk.
- Verify with evidence matched to the contract, not a universal checklist.
- Never place secrets in helpers, commands, manifests, logs, or retained
  artifacts.

For hybrid work, verify the future durable behavior and historical transition
separately.

## Retain Or Clean

Codex may delete the exact disposable scratch files or directory that it created
for the current task once they are no longer needed. Before deletion, confirm
that the target is task-created scratch rather than a canonical input, formal
deliverable, pre-existing file, shared path, or unknown item.

Retain task-created scratch when failure recovery, reproduction, retry, audit,
or handoff still benefits from it. Report the retained path and purpose. A
project-wide, shared, pre-existing, or ambiguous cleanup requires explicit
scope.

For a retained helper, record only:

- purpose;
- inputs;
- outputs;
- how to use it; and
- when it may be deleted.

Promotion into maintained code is a separate durable change. Require a real
future owner and the project's normal tests and documentation; possible reuse
alone is not enough.

## Report

Report the durable, temporary, or hybrid split; relevant helper and output
paths; verification performed; scratch retained or removed; and any unresolved
recovery or cleanup boundary. A helper passing does not establish overall task
completion.

Read references/source-notes.md only when maintaining this skill.
