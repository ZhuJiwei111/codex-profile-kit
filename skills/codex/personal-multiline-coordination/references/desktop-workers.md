# Desktop Workers And Supervision

## Surface Selection

Choose a Desktop-visible worker task when a line:

- is a top-level implementation stream;
- needs its own worktree and branch;
- benefits from a user-visible lifecycle in the Desktop app;
- may pause, resume, or require iterative rework;
- should remain independently inspectable after coordinator intake.

Choose a managed subagent for a bounded exploration, review, focused
validation, helper, or ordinary integration-conflict analysis. A subagent does
not become a hidden replacement for an approved Desktop worker.

If the current tool surface cannot create or operate the requested Desktop
worker, report the unavailable capability. Keep the line `planned`; do not
claim it was launched and do not silently change surfaces.

## Launch Sequence

Before creating visible workers:

1. verify the launch manifest and authorization;
2. prepare canonical worktrees only for currently ready lines;
3. verify each worker's base OID, branch, and exclusive paths;
4. create only currently ready tasks;
5. send one line card to each task;
6. record returned task identifiers in the live snapshot, if one is needed;
7. tell the user which lines are active and which event will cause intake.

For a dependent line, defer its worktree and task until predecessor checkpoints
are accepted and integrated. Create it from the resulting integration OID; do
not create a stale planned worktree and later repoint it invisibly.

Task creation is user-visible external state. A generic request for read-only
analysis, an implicit trigger, or a discussion does not authorize it.

## Worker Rules

A worker:

- stays in the assigned `cwd` and branch;
- owns only its declared paths and outputs;
- may run only granted resource actions;
- stops at its line-card condition;
- does not commit, integrate, operate other workers, launch successors, or
  decide the line result;
- reports evidence and a `recommended_outcome`.

If the worker discovers that its base, worktree, ownership, dependency, or
resource assumptions are wrong, it stops and reports the mismatch.

## Event-Driven Supervision

Prefer these wake events:

- a worker returns a report;
- a worker task changes to a terminal or waiting state;
- a delegated tool call completes;
- a long-job monitor reports a material transition;
- the user changes scope or grants authority;
- a dependency line receives a coordinator decision.

Use bounded waits supplied by the coordination surface. Do not run fixed-rate
poll loops, repeatedly list every worker, or keep a terminal open only to watch
state. A wait timeout is a chance to hand control back, not evidence that the
worker failed.

## Intake And Rework

On an event:

1. read the worker report;
2. inspect only the relevant task, worktree, diff, outputs, and evidence;
3. distinguish worker state from line decision;
4. set `pass`, `no-go`, `needs-more-evidence`, or `blocked`;
5. request bounded missing evidence or rework when needed;
6. schedule only successors whose dependencies and conflicts now permit them.

Reuse a worker for bounded rework in its existing worktree. Create a replacement
only when the original task or workspace cannot safely continue. Never point an
existing worker at another worktree.

## Model And Reasoning Controls

Treat model and reasoning intensity as capabilities, not promises. When the
task-creation surface exposes them, choose them per line risk and uncertainty;
do not derive them from the coordinator's current setting. Monitoring and
mechanical checks normally need less reasoning than design, debugging, or
integration review. If the surface does not expose a control, omit it and do
not claim a switch occurred.

## Evidence Boundary

The local auditor cannot prove that a Desktop task exists, belongs to this host,
or has a particular live state. Reconcile those facts through the current-host
Desktop task surface, and keep other-host records out of context and output.

No live Desktop worker smoke test was performed for this skill revision; that
test requires separate authorization and an exposed task-creation capability.
