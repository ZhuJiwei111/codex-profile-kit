# Recovery, Decisions, And Checkpoints

Borrow Trellis-style memory without adopting Trellis as a dependency.

## Checkpoints

Write checkpoints only at gates:

- Line proposed or activated.
- Worker stopped for intake.
- Coordinator accepted `pass`, `no-go`, `blocked`, or `needs-more-evidence`.
- Line became `finish_candidate`.
- Line was archived or revived.

Checkpoint entries should be short: line id, status, decision, evidence paths, next safe action, and updated timestamp.

## Decision Records

Use compact traces for state-changing decisions:

- Opening or splitting lines.
- Archiving or restarting drifted work.
- Marking `pass`, `no-go`, `blocked`, `needs-more-evidence`, or `finish_candidate`.
- Changing scope, owner, cwd, branch, exclusive files, or stop condition.
- Launching, pausing, or interpreting a long-running job line.
- Choosing merge or finish strategy.

Record:

- decision id
- timestamp
- line id
- decision
- rationale summary
- evidence paths
- risks
- reversible or irreversible consequences

Do not store full chain-of-thought, long logs, secrets, raw credentials, or large command output. Store paths and compact summaries.

## Recovery Queue

Capture recoverable work broadly, but keep entries compact:

- stale or abandoned worktrees
- blocked or no-go lines with reusable artifacts
- old worker handoffs
- promising ideas not chosen
- partial experiments
- artifact paths that may matter later

Each entry should include:

- recovery id
- source line or worker
- why it was deferred
- reusable evidence or artifact paths
- revive condition
- archive condition
- last reviewed timestamp

Check the queue during audit, coordinator intake, blocked/no-go decisions, and before creating a similar new line. Do not check it on every ordinary turn.

## Gate Archive

Archive active decision/recovery material at semantic gates: finish, no-go, blocked closure, line archive, or major stage change. Keep an active index pointing to archive paths so old work remains discoverable without bloating the active registry.
