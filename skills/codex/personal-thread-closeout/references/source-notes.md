# Source Notes

Checked: 2026-07-16

## Provenance Decision

- Classification: local-origin personal workflow.
- Primary source: the user's recurring need to review finished Codex tasks,
  preserve durable lessons, update project documentation only when worthwhile,
  and archive exact targets without losing the controller audit trail.
- No external retrospective or thread-management skill text, script, or runtime
  package is copied.

## User-Locked Design Decisions

- Explicit `$personal-thread-closeout` invocation is required in a separate
  external controller task.
- Entry may name one exact target, an ordered exact-target list, or an explicit
  current-host project sweep.
- The controller never targets itself and remains alive to report results.
- Exact target lists are sequential and first occurrence wins for duplicates.
- Each target is assessed independently; target-local failure continues, while
  shared infrastructure failure stops later mutation.
- Project sweep is fail-closed, exact-project and current-host only. Its default
  selects tasks older than 15 full local-calendar days, oldest first, maximum 10.
- Persistent writes are limited to each target's project and only when their
  value and verification gates pass.
- Personal profile surfaces receive proposals only.
- Documentation is conditional; short tasks and failures without new knowledge
  may close without a new document.
- Prefer an existing project convention; otherwise use one unique
  `docs/retrospectives/<date>-<task-slug>.md` record.
- Archive uses the exact ID as that target's final state-changing action.

## Local Profile Evidence

The initial single-target design used profile-kit revision
`1958e80b1af61cc5437d95e844a95eaf55aadef8` as its collaboration baseline. Its
portable instructions and then-current verification, documentation, and branch
contracts were design evidence, not bundled runtime dependencies. The current
revision replaces retired routing names with bounded core behavior or active
owners.

## Live Self-Archive RED

On 2026-07-13 an early invocation archived its own calling task. The target
became archived, the closeout turn became `interrupted`, and no final result or
direct confirmation was recorded. A separate controller later unarchived the
target and read the interrupted turn by exact ID.

This is direct evidence that self-archive cannot satisfy the result contract.
The workflow therefore requires a different controller and exact target IDs.

## Product-Surface Evidence

The 2026-07-13 observation established native exact-target read and archive
actions. The later project-sweep design additionally requires a native bounded
task-list surface; this reference does not claim that every controller exposes
one. These capabilities are environment-owned and must be rechecked at runtime:

- read and archive explicit targets by exact ID;
- enumerate only for an explicit project sweep;
- filter current host and exact project before target content enters context;
- treat the archive tool result as the only direct archive evidence; and
- keep the controller alive to report it.

This never authorizes raw transcript access, cross-host management, or treating
archive as proof of completion.

## Rejected Designs

- implicit invocation at every task ending;
- self-archive or omission of target IDs;
- title-only search or broad enumeration outside explicit project sweep;
- mandatory documentation for short or non-informative failures;
- one cumulative global lessons file across projects;
- automatic personal-profile mutation;
- automatic implementation, Git, publication, worker, or job actions;
- batch-wide rollback or stopping on a target-local failure; and
- claiming archive success without the native action result.
