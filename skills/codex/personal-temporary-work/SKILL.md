---
name: personal-temporary-work
description: Use when one-off migration, conversion, or artifact work might otherwise add permanent code; split the minimal durable change from an excluded temporary helper, and clean or promote it only under the explicit lifecycle contract.
---

# Personal Temporary Work

Protect maintained code from one-off transition logic. Separate what future
normal operation must keep from what is needed only to migrate, convert, repair,
inspect, or post-process existing state.

## Split Steady State And Transition Work

Classify the request before adding a branch, flag, module, parameter, or API:

- **Steady state:** future normal users need it. Make the smallest coherent
  durable change through its implementation owner.
- **Transition:** a bounded existing dataset, artifact set, or local state needs
  one-time treatment. Prefer a temporary helper outside maintained code.
- **Hybrid:** change future behavior minimally and use a temporary helper for
  historical state.
- **Durable migration surface:** promote only when repeated operators,
  environments, releases, versions, rollback, or support need it.

Skip this workflow for a direct command that creates no helper or artifact. Do
not use temporary placement to evade a normal durable feature. For an explicit
one-off case with no ongoing-support evidence, default to the temporary helper.
Read [durable versus temporary](references/durable-vs-temporary.md) when the
boundary is consequential or unclear.

## Lock Ownership And Transformation

Before creating files, identify:

- owning project/worktree, applicable instructions, and task-owned paths;
- canonical inputs, immutability, and provenance;
- formal deliverable, helper, evidence, staging, and cleanup candidates;
- ordering, format, overwrite, interruption, recovery, and acceptance;
- environment, scale, resources, and retention decision.

Use bounded core repository inspection when root, convention, dirty overlap, or
output ownership is unclear. Ask one decision-changing question when ambiguity
changes semantics, placement, destructive behavior, or scope.

Prefer regeneration when an affordable deterministic canonical generator owns
the output. Prefer direct transformation when regeneration is unavailable or
materially costlier and contract-relevant equivalence can be checked.

## Place And Exclude Temporary Work

Follow an existing project scratch convention. Otherwise use:

```text
<owning-project-or-worktree>/tmp/<task-slug>/
```

An independently managed monorepo subproject may use its own task `tmp/` only
when it fully owns the work. Keep formal deliverables at their explicit output
paths and use output-adjacent staging when same-filesystem publication or
capacity requires it. Workers keep scratch in their own worktrees.

Temporary state is excluded by default from:

- Git tracking and ordinary delivery diffs; and
- normal search, test, lint, typecheck, build, and package inputs.

When creating a project-root `tmp/` for the first time, add exact `/tmp/` to the
applicable `.gitignore` if no tracked `tmp/` content or conflicting convention
exists. If tracked content, overlapping rules, multiple owners, or ambiguity
exists, ask first. Change other tool exclusion config only after observing that
the actual tool includes task `tmp/`; do not preemptively edit every scanner.

Do not hide helpers in source directories or use a host-global temp directory
for traceable work by default. Exclusion from Git never authorizes stage, commit,
or deletion.

## Annotate Helper Lifecycle

A helper that may be retained or promoted must carry a concise top-of-file
comment, adapted to project convention but preserving these meanings:

```text
Purpose:
Lifecycle:
Background:
Inputs:
Outputs:
Safety:
Usage:
Environment:
Verification:
Limitations:
```

For formats that cannot contain comments, place the same contract in the
smallest adjacent README or manifest and link it from the helper name or usage
record. The annotation is not throwaway boilerplate: it remains after promotion
so future operators understand the one-off origin and limits.

## Execute And Verify

- Keep canonical inputs immutable and write a new output by default. Treat
  overwrite, in-place rewrite, and deletion under their destructive boundary.
- Reuse stable project utilities, but do not add a production API only for the
  helper.
- Use dry run, sample, staging, or manifest when it materially reduces risk.
- Verify the actual contract with relevant counts, keys, schemas, checksums,
  ordering, semantic comparisons, sampled reads, or consumer checks.
- Treat helper code as task-owned code: explicit inputs, bounded side effects,
  safe failure, and no secrets.
- Follow global authorization for installation, large artifacts, destructive
  replacement, heavy resources, and long-running execution.

Verify durable steady-state behavior and historical transition separately in a
hybrid change. Neither half proves the other.

## Manual Cleanup Contract

Success or verification never triggers ordinary cleanup automatically.

- If the user explicitly says “clean tmp” without a broader scope, that
  authorizes cleanup only of the current task-owned `tmp/<task-slug>`.
- If ownership is unclear, perform a read-only inventory and ask. Do not delete
  by path name alone.
- Project-wide or multi-task cleanup requires explicit scope.
- Clean exact task-owned paths; never clear an entire project `tmp/`, system temp,
  cache, formal deliverable, canonical input, pre-existing file, or unknown item
  by inference.
- Sensitive task-created temporary files are the exception: remove them promptly
  after their required use through the authorized mechanism and report the safe
  path/category, never the value.

An explicit cleanup request needs no second per-file approval when every selected
path is inside the already authorized current task directory and ownership is
clear. Report retained and removed paths.

## Retain Or Promote

Retain a small non-sensitive helper, manifest, or evidence only when it supports
audit, reproduction, retry, or recovery. Retention does not make it tracked or
part of the formal deliverable.

Promotion is a separate durable mutation. Require positive evidence of a normal
future owner, then move the helper into the project's established convention or
`scripts/one-off/<task-slug>/`. Add appropriate tests, docs, compatibility,
rollback, and maintenance ownership. Keep the lifecycle annotation after
promotion. Promotion still does not authorize Git stage or commit.

## Report The Handoff

Report exact paths, command and environment owner, transformation boundary,
verification, exclusions, cleanup scope, and anything not run. Use a small
manifest only when repeated runs or handoff require it.

If ordinary retained tmp actually remains, end with exactly one compact line
containing its path, purpose, approximate size, and `manual-retention`. Omit that
line when no retained tmp remains. A helper pass never proves the overall task
complete.

## Ownership Boundaries

- `personal-brainstorms` resolves a consequential durable-versus-temporary
  choice when evidence does not decide it.
- Core task inspection resolves project root, worktree, conventions, and dirty
  overlap.
- Domain workflows own debugging hypotheses, context use, small project-doc
  edits, code simplification, tests, and artifact semantics. This skill owns only
  helper placement, exclusion, lifecycle annotation, cleanup, and promotion.
- `personal-subagent-boundaries` owns delegation and
  `personal-multiline-coordination` owns worktrees and shared data bindings.
- Global instructions own long-job/resource/destructive/sensitive boundaries;
  ordinary status uses one bounded core read-only check.
- `personal-risk-verification` owns the final verdict and
  `personal-branch-finish` owns later Git readiness.

See [source notes](references/source-notes.md) for provenance and local design
evidence.
