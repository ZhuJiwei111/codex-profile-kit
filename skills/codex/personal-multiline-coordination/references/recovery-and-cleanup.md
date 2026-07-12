# Recovery And Cleanup

## Reconcile Before Acting

Build a read-only view from:

1. current-host Desktop task facts, when the task surface is available;
2. `git worktree list --porcelain`, branches, refs, HEADs, status, and
   interrupted-operation markers;
3. the coordinator's current context;
4. an optional schema-v2 snapshot;
5. an approved file-backed planning handoff, if the work crosses sessions.

Do not recreate the removed `.codex/multiline` registry or recovery queue.

Run the auditor without a snapshot for inventory, or with `--snapshot ...
--check` for reconciliation. The auditor is local and read-only; it does not
prove Desktop task state.

## Common Mismatches

- task exists but worktree is missing;
- worktree exists but the task is unavailable;
- task `cwd`, declared branch, or declared HEAD differs from Git;
- two active writers claim one worktree or overlapping paths;
- dependency, output, or resource conflicts were overlooked;
- a worker stopped without a report;
- merge, rebase, cherry-pick, or revert is interrupted;
- a checkpoint exists but is not integrated or preserved;
- an immutable-data link is broken, unignored, misdirected, or shadows a tracked
  path;
- a supposedly disposable worktree is dirty.

## Preservation-First Response

For a mismatch:

1. stop new scheduling into the affected area;
2. capture task ids, worktree paths, branches, HEADs, status counts, operation
   markers, and available handoffs;
3. distinguish unavailable evidence from evidence of failure;
4. keep dirty worktrees, branches, refs, logs, and artifacts intact;
5. identify the smallest safe reconciliation or user decision;
6. restart or replace a line only from a clean, visible base.

Never tell an existing worker to change its canonical worktree. Never abort an
interrupted Git operation until its intent and preservation path are understood
and the action is authorized.

## Replacement

Use the same Desktop worker for bounded rework when its task and worktree are
healthy. Use a new Desktop worker when the old lifecycle is unavailable or the
line requires a clean restart. Use a managed subagent only for bounded recovery
inspection or conflict analysis, not as a hidden replacement for an approved
top-level line.

Record why replacement was needed, which OID/path it starts from, and what
happens to the preserved original.

## Conditional Cleanup Grant

A launch manifest may request a conditional grant for named worktrees. Before
using it, recheck every condition:

- line closed and terminal decision recorded;
- task stopped or handoff complete;
- worktree clean;
- checkpoint integrated with an OID mapping or preserved by a named ref;
- no active dependency or mutable output consumer;
- no interrupted Git operation;
- path exactly matches the granted candidate.
- the candidate is coordination-owned and is neither the primary worktree nor
  the integration worktree.

Without all conditions, preserve and report. A stale snapshot never overrides
current Git evidence.

## Never Automatic

Do not automatically:

- permanently delete a Desktop task;
- force-remove a worktree;
- run global worktree prune;
- delete a branch or preservation ref;
- discard a dirty diff;
- abort merge/rebase/cherry-pick/revert;
- remove project source data behind a link;
- erase logs or artifacts with unresolved audit value.

Archiving a visible task, deleting a branch, or removing preserved evidence
requires exact authority even after a worktree is safely removable.

## Recovery Output

Report:

- observed Desktop and Git facts, with unavailable sources marked;
- mismatches and their consequences;
- evidence preserved and exact paths/OIDs;
- safe immediate action;
- action requiring new authority;
- event or decision that should resume scheduling.
