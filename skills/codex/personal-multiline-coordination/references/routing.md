# Workflow Routing

## Entry Routing

| Situation | Owner |
| --- | --- |
| Explicit multi-worker/worktree execution | `personal-multiline-coordination` |
| Existing worker/worktree ambiguity without execution request | this skill, read-only audit only |
| One bounded subagent delegation | `personal-subagent-boundaries` |
| Consequential decomposition or architecture choice | `personal-brainstorms` |
| Ordinary unresolved requirements | normal targeted questions; `personal-brainstorms` when consequential |
| Explicit `$personal-grilling` invocation | `personal-grilling` (manual-only) |
| Explicit file-backed planning request | `personal-planning-with-files-zh` |
| Ordinary one-time long-job status request | bounded read-only status path |
| Explicit `$personal-long-job-status` invocation | `personal-long-job-status` (manual-only) |
| Unexpected failure or failed repair attempt | `personal-evidence-debugging` |
| Final evidence-backed completion decision | `personal-risk-verification` |
| Formal Git readiness, user commit/PR choice, or handoff | `personal-branch-finish` |

Multiline coordination remains the coordinator when it invokes an adjacent
skill. The adjacent skill owns only its specialized decision or artifact.

## Worker Versus Subagent

Use a Desktop-visible worker task for a top-level implementation line with its
own worktree and lifecycle. Use a managed subagent for bounded exploration,
review, validation, helper work, monitoring, or ordinary conflict analysis.

Follow `personal-subagent-boundaries` for managed-subagent context, file
ownership, stop, and reporting. This skill adds the global dependency,
worktree, resource, and intake decisions.

## Planning And Context

- Current-task coordination needs no persistent registry.
- Cross-session coordination alone does not authorize `.planning` files.
  Default to a reproducible handoff, optionally using an existing snapshot.
- Route to `personal-planning-with-files-zh` only after an explicit request for
  file-backed planning; that skill then owns the plan root and artifacts.
- Use `personal-context-compression` to produce a compact continuation summary;
  it does not write or restore state.
- Use `personal-context-save-restore` only for an explicit immutable
  cross-session packet; restoring it never launches workers or mutates Git.

## Verification And Finish

Worker checks are line-local evidence. Integration checks are stage evidence.
Neither is the final completion verdict.

After all accepted lines are integrated, use `personal-risk-verification` as
the only final completion gate. If it supports handoff, use
`personal-branch-finish` for branch/worktree readiness and explicit user Git
decisions. This skill does not push, open PRs, or merge.

## Long Jobs

This skill schedules authorized long-job lines and records their resource
contracts. Durable launch and monitoring rules still apply. Handle an ordinary
one-time status or ETA request through a bounded read-only inspection. The
manual-only `personal-long-job-status` skill requires the user to invoke
`$personal-long-job-status` explicitly; it does not become the coordinator or
monitor.

## Conflict Routing

1. Tiny deterministic integration conflict: coordinator, within grant.
2. Bounded independent conflict analysis: managed subagent.
3. Substantive implementation rework: Desktop-visible worker.
4. Cross-line design conflict: ask the user a normal targeted question, using
   `personal-brainstorms` when consequential. Route to `personal-grilling` only
   when the user explicitly invokes `$personal-grilling`.

The coordinator records the result and reschedules affected lines.

## Current Compatibility Contract

Do not recreate a permanent multiline registry or `finish_candidate`. Formal
Git readiness consumes the current coordinator intake, authoritative decision,
and integration provenance through `personal-branch-finish`.
