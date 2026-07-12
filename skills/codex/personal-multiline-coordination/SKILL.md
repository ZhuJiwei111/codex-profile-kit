---
name: personal-multiline-coordination
description: Coordinate parallel Codex worker lines across visible tasks, isolated Git worktrees, resources, intake, integration, and recovery. Use for explicit multiline/worktree execution or ambiguous worker/worktree ownership; implicit use is read-only only.
---

# Personal Multiline Coordination

## Mission

Act as the coordinator for parallel repository work whose worker, worktree,
dependency, integration, or resource ownership would otherwise be ambiguous.

Keep a star topology:

- the coordinator owns the global plan, scheduling, intake, and authoritative
  line decisions;
- each writer owns one bounded line and one canonical worktree;
- workers report evidence and a `recommended_outcome` of `accept`, `reject`,
  or `needs-more-evidence`, but do not decide the coordination line's result;
- cross-line decisions return to the coordinator or user.

This skill does not create a permanent multiline registry. Current truth comes
from Desktop task state, Git state, and an optional lightweight coordinator
snapshot.

## Entry And Authority Gate

Classify the entry before acting.

### Explicit execution

An explicit request to coordinate or execute multiple worker/worktree lines
authorizes the non-destructive Desktop worker tasks and Git worktrees named in
one reviewed launch manifest. It does not authorize commits, integration,
cleanup, heavy resources, monitoring, publication, or destructive recovery
unless the manifest grants those actions precisely.

### Explicit audit or discussion

Inspect and reason only. Do not create tasks, worktrees, snapshots, branches,
or symlinks, and do not operate existing workers.

### Implicit trigger

When this skill triggers because existing workers or worktrees create risk,
start with the read-only audit and report the mismatch. Do not write state or
operate workers until the user confirms execution.

Run:

```bash
python3 "$HOME/.codex/skills/personal-multiline-coordination/scripts/audit_multiline.py" <project-root> --json
```

Add `--snapshot <file-or-> --check` only when a schema-v2 coordinator snapshot
already exists or is supplied through stdin.

## Select The Execution Surface

Use a Desktop-visible worker task for a top-level implementation line that
needs an independent lifecycle, durable user visibility, or an isolated
worktree.

Use a managed subagent for bounded, one-shot work such as exploration, review,
validation, helper work, or ordinary conflict resolution. Follow
`personal-subagent-boundaries` for its prompt and reporting contract.

The coordinator may resolve a tiny deterministic integration conflict locally.
Route substantive rework that needs its own iteration history back to a
Desktop-visible worker. Route cross-line design conflicts to the user, using
`personal-brainstorms` when the decision is consequential.

Do not silently substitute a managed subagent when the approved manifest calls
for a Desktop worker but the required task capability is unavailable. Report
the capability gap and preserve the line as planned.

## Coordination Workflow

1. Establish the repository root, applicable instructions, current branch,
   worktree inventory, relevant dirty state, and interrupted Git operations.
2. Decompose work into top-level lines. Record dependencies, write sets, output
   paths, resource claims, acceptance criteria, and stop conditions.
3. Build both a dependency graph and a conflict graph. A conflict exists when
   active lines overlap in writes, outputs, exclusive resources, or mutable
   project data.
4. Present one launch manifest. Include every task/worktree creation plus any
   separate integration, resource, monitoring, or cleanup grant being sought.
5. Prepare worktrees only for currently ready writers, from their resolved base
   OID. Keep future task/worktree creation authorized but deferred. Bind readers
   to a fixed revision and avoid unnecessary reader worktrees.
6. Launch only currently ready and non-conflicting lines. Give each worker its
   line card and no broader authority.
7. Wait for events or handoffs. Intake evidence, inspect Git state and outputs,
   then set the coordinator decision: `pass`, `no-go`,
   `needs-more-evidence`, or `blocked`.
8. Schedule newly unblocked lines. Do not use a fixed worker count when the
   dependency, conflict, or resource graphs imply a different safe level.
9. Under an exact integration grant, create a source checkpoint and integrate
   it through the dedicated integration worktree. Record source and integrated
   OIDs.
10. Run the final completion gate through `personal-risk-verification`, then
    route formal Git readiness or user-directed commit/PR handling to
    `personal-branch-finish`.

Read `references/contracts.md` before producing a launch manifest, line card,
snapshot, worker report, or coordinator intake.

## Workspace Rules

A writer's canonical `cwd`, branch, and worktree are immutable for that worker
task. Never redirect an existing writer to another worktree. Restart or hand
off from a clean, visible state instead.

Resolve worktree placement in this order:

1. explicit user path;
2. repository instructions or established convention;
3. Desktop-native placement;
4. an applicable `HOST_LOCAL.md` override;
5. repo-sibling fallback:
   `<repo-parent>/.codex-worktrees/<repo-name>/<coordination-id>/`.

The fallback contains `integration/` and `workers/<line-id>/`. Do not place
fallback worktrees inside the repository or under `~/.codex`.

Read `references/worktree-integration.md` before creating worktrees, sharing
project-local data, checkpointing, integrating, or resolving conflicts.

## Event-Driven Supervision

Supervise through worker lifecycle events, completed tool calls, handoffs, and
bounded waits. Do not periodically poll every worker, tail logs continuously,
or duplicate a monitor's checks.

The coordinator may perform a bounded read-only intake check when a worker
reports or appears to stop. It should then decide, request specific missing
evidence, or wait for the next event.

Worker silence is not evidence of failure. Use recovery reconciliation before
restarting or replacing a worker.

Read `references/desktop-workers.md` before launching, waiting on, resuming, or
replacing Desktop-visible workers.

## Integration Boundary

Workers do not commit. They stop with a dirty or clean line worktree plus a
structured report.

Only the coordinator may, under an explicit local integration grant:

- inspect and accept the exact line diff;
- stage only task-owned paths;
- create the source checkpoint commit on the line branch;
- integrate it into the dedicated integration branch, normally by
  cherry-pick;
- record the source checkpoint OID and resulting integrated OID.

If a cherry-pick or rebase stops for a conflict and the coordinator stages any
manual resolution, record the completed integration as `method: manual`, not
as the command that initiated it. Preserve the source checkpoint with a named
`preservation_ref`; manual integration cannot mechanically prove source-patch
equivalence or make that checkpoint disposable by itself.

An internal checkpoint is not final Git readiness and does not authorize a
user-facing commit, merge, push, PR, or publication.

## Resource And Monitoring Grants

Treat high-traffic downloads, heavy GPU use, long-job launch, active
monitoring, repair/restart, and next-stage launch as separate resource actions.
They may be granted per line or stage in the launch manifest; do not infer one
from another.

A monitoring worker is read-only. It reports evidence and never repairs,
restarts, stops, mutates outputs, launches a next stage, or makes a line
decision unless an exact contingency was preauthorized.

Read `references/resource-grants.md` before scheduling constrained resources or
long-running lines.

## Recovery And Cleanup

Reconcile Desktop facts, Git/worktree facts, interrupted operations, and any
available snapshot before changing state. Default to preservation.

Do not automatically delete a Desktop task permanently, force-remove a
worktree, prune globally, discard a dirty tree, delete a branch, abort an
operation, or erase project data.

A conditional cleanup grant may cover named clean, closed, integrated or
otherwise preserved line worktrees. It never covers source project data behind
a symlink; cleanup removes only the approved link or worktree.

Read `references/recovery-and-cleanup.md` before recovery, replacement, or
cleanup.

## Persistence

Keep live coordination state in current task context when practical. Use a
small schema-v2 snapshot only when reconciliation or handoff benefits from a
machine-checkable view.

For cross-session work, promote the brief and snapshot into the approved
`.planning/<plan-id>/` plan through `personal-planning-with-files-zh`. Do not
create `.codex/multiline`, a shadow registry, or a second source of truth.

## Output

Return the smallest useful artifact for the current gate: an audit summary,
launch manifest, line card, coordinator intake, integration record, recovery or
cleanup recommendation, or final coordination handoff.

State what remains unverified, what needs new authority, and which event should
wake the coordinator next.

## Reference Routing

- `references/contracts.md`: state axes and artifact schemas.
- `references/desktop-workers.md`: visible worker lifecycle and supervision.
- `references/worktree-integration.md`: layouts, bindings, integration, conflicts.
- `references/resource-grants.md`: heavy resources, long jobs, and monitoring.
- `references/recovery-and-cleanup.md`: reconciliation and safe cleanup.
- `references/routing.md`: adjacent skill ownership and handoffs.
- `references/source-notes.md`: provenance, environment evidence, adopted
  ideas, rejected ideas, and validation limits.
