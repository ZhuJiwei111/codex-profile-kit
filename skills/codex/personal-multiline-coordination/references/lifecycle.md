# Line Lifecycle

Use stage gates so workers stop at evidence boundaries instead of inventing the next stage.

## Statuses

- `proposed`: candidate line exists, but Line Card is incomplete or not approved.
- `active`: worker or coordinator is executing the bounded line in its canonical worktree.
- `waiting_intake`: worker reached a stop condition and wrote handoff.
- `pass`: coordinator accepted evidence for the line objective.
- `no-go`: coordinator rejected the line as not worth continuing.
- `blocked`: line cannot proceed without user input, external state, or a new plan.
- `needs-more-evidence`: evidence is insufficient; coordinator must define the next evidence request.
- `finish_candidate`: pass + handoff + verification + coordinator intake are complete.
- `archived`: line is closed, superseded, or preserved for traceability.

## Start Or Continue A Line

1. Audit current worktrees, cwd, branch, registry, and handoff paths.
2. Check the Recovery Queue before creating a new line when the objective resembles stale, blocked, or no-go work.
3. Require a Line Card before work begins.
4. Ensure active editing, long jobs, or worker activity happen in a canonical worktree.
5. Give each worker one actual cwd, one branch, one line, exclusive editable paths, stop condition, handoff path, and maximum productive continuation budget.

## Intake

When a worker stops, intake evidence instead of continuing blindly:

- Read the line-local handoff.
- Check changed paths and git state for the canonical worktree.
- Check verification output and skipped checks.
- Compare results against the Line Card.
- Decide `pass`, `no-go`, `blocked`, `needs-more-evidence`, `finish_candidate`, or `archived`.

## Drift Recovery

Treat mismatched cwd, branch, thread ownership, handoff paths, or registry state as drift.

Default response:

1. Preserve evidence: thread id when available, cwd, branch, head, git status summary, tracked diff summary, untracked file list, handoff paths, and artifact manifest.
2. Do not ask an existing worker to edit a different worktree.
3. Archive the unclear line or worker state.
4. Restart from a fresh Line Card and visible canonical worktree.

## Finish Gate

A line may become `finish_candidate` only when:

- The worker reported `pass`.
- The handoff exists and names changed paths, commands, verification, artifacts, risks, and recommended next action.
- Coordinator intake agrees the Line Card is satisfied.
- Cross-line conflicts are checked or explicitly recorded as remaining risk.

After this gate, route to `personal-branch-finish` for commit, PR, merge, or final handoff decisions. Do not commit, PR, merge, or declare project completion from this lifecycle alone.
