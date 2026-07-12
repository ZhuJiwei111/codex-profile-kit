# Workflow Routing

## Entry Routing

| Situation | Owner |
| --- | --- |
| Explicit multi-worker/worktree execution | `personal-multiline-coordination` |
| Existing worker/worktree ambiguity without execution request | this skill, read-only audit only |
| One bounded subagent delegation | `personal-subagent-boundaries` |
| Consequential decomposition or architecture choice | `personal-brainstorms` |
| Critical unresolved requirements | `personal-grilling` |
| Cross-session planning files | `personal-planning-with-files-zh` |
| One-time long-job status request | `personal-long-job-status` |
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
- When a coordination run must cross sessions, ask
  `personal-planning-with-files-zh` to own the plan root and store a compact
  brief plus optional snapshot there.
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
contracts. Durable launch and monitoring rules still apply. Use
`personal-long-job-status` only when the user asks for a one-time read-only
status/ETA; it does not become the coordinator or monitor.

## Conflict Routing

1. Tiny deterministic integration conflict: coordinator, within grant.
2. Bounded independent conflict analysis: managed subagent.
3. Substantive implementation rework: Desktop-visible worker.
4. Cross-line design conflict: user decision, usually with
   `personal-brainstorms`; use `personal-grilling` for decision-changing unknowns.

The coordinator records the result and reschedules affected lines.

## Current Compatibility Contract

Do not recreate a permanent multiline registry or `finish_candidate`. Formal
Git readiness consumes the current coordinator intake, authoritative decision,
and integration provenance through `personal-branch-finish`.
