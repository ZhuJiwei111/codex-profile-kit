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
| Ordinary one-time long-job status request | one exact read-only executor pass, then main-process intake |
| Unexpected failure or failed repair attempt | `personal-evidence-debugging` |
| Final evidence-backed completion decision | `personal-risk-verification` |
| Local Git readiness, local-only commit, preservation, or handoff | `personal-branch-finish` |
| Authorized GitHub commit/push/PR publication flow | `github:yeet` |

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
- For continuation of an existing visible task, require its exact task id and a
  current-host metadata precheck through the exact-target task read operation.
  The main process builds the bounded continuation packet defined in
  `desktop-workers.md`; it does not enumerate unrelated tasks, restore an
  archive, or forward an unbounded conversation.
- If the exact task or current-host identity cannot be verified, stop and ask
  for the exact target. Continuation never implies worker launch, Git mutation,
  resource use, or stage progression.

## Verification And Finish

Worker checks are line-local evidence. Integration checks are stage evidence.
Neither is the final completion verdict.

After all accepted lines are integrated, use `personal-risk-verification` as
the only final completion gate. If it supports handoff, use
`personal-branch-finish` for local branch/worktree readiness, preservation, or
a local-only commit. Use `github:yeet` for an authorized GitHub publication;
branch finish must not commit first. This skill does not push, open PRs, or
merge.

## Long Jobs

This skill schedules authorized long-job lines and records their resource
contracts. Durable launch and monitoring rules still apply. Handle an ordinary
one-time status or ETA request through one exact read-only executor inspection,
followed by main-process intake. It never becomes recurring monitoring.

## Conflict Routing

1. Tiny deterministic integration conflict: coordinator grants the exact
   resolution; integration executor applies it.
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
