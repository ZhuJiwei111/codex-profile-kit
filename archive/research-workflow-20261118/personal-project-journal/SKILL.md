---
name: personal-project-journal
description: Record a durable project event in an existing repository JOURNAL; initialize a journal only during independently authorized repository writes. Excludes routine discussion and unchanged status checks.
---

# Personal Project Journal

Keep a concise, human-readable history of changes, decisions, failures, and
outcomes that affect future work. JOURNAL owns chronological event history;
plans own current task state and project documents own durable decisions.

## Use the existing owner

Locate the Git root and the applicable journal or work-line instructions.
Read the local journal guide, file-ownership table, and relevant recent entry
before writing. Do not write a synchronized read-only copy merely because it
is named JOURNAL.md. Preserve
existing single-file, work-line, monthly, and experiment-card conventions.
Follow the repository's assigned event owner; by default the main task writes
the journal and workers return evidence to that owner.
An incidental dependency or read-only SSH reference needs no journal entry.

If no journal exists, initialize only within an already-authorized repository
write, using `assets/journal-index.md`, `assets/journal-readme.md`, and
`assets/journal-month.md`. Substitute the local calendar month. Do not initialize a journal during a read-only task. Respect an existing ignore rule; do not
change tracking policy or backfill earlier work without a request.

## Record the consequential delta

A durable project event includes a material repository change, user decision,
confirmed root cause or blocker, costly failure, consequential handoff, or
completed outcome. Routine browsing, explanation, repeated status, and unchanged
verification do not qualify. Existing journal maintenance is a narrow standing
write exception; it grants no authority outside the journal-owned paths.

Use the project's entry shape. For a new monthly journal:

```markdown
## <local ISO-8601 timestamp with offset> · <high|medium|routine> · <topic>

<what changed or was decided, and why it matters>

- **证据**：<the relevant result and its source, when useful>
- **后续**：<only a material unresolved item and its owner, when one remains>
```

- `high`: authority, scope, consequential decisions, critical gates, root causes,
  expensive pitfalls, and handoffs; preserve rationale and impact.
- `medium`: material implementation, changed risk, or phase outcome.
- `routine`: ordinary durable maintenance; one to three sentences is enough.

Keep one coherent task entry rather than opening a new event for every command
or verification. Update an explicitly active entry at meaningful phase changes;
append the new verified delta without erasing earlier facts. Preserve a frozen
entry's meaning; correct a material mistake in a dated note or new entry.
Repository-specific status headings and lifecycle rules take precedence.
Archive by continuing relevance, preserving the original facts and a pointer;
keep unresolved work in its existing active owner. Archival is not completion.

For already-authorized long-running work, record actual start and meaningful
phase changes without waiting for completion. Include the stage, owner, output,
resource or budget boundary, and next check when relevant. A planned next stage
is not a started stage; an ended chat is not proof that its process stopped.
At handoff, leave unresolved work with a named TODO, plan, card, or successor.

## Save and close

Use the existing insertion point. In the bundled monthly layout, insert entries
below `<!-- journal-entries -->` and new month links below `<!-- journal-months -->`,
newest first. Make writes atomically and read back the inserted anchor.

Record what is actually saved, tested, committed, pushed, or running; these are
different states. Never predict a future commit or push. For ongoing work,
point to the existing task/plan/card owner; record a blocker, recovery condition,
or handoff only when consequential. Do not duplicate the active task board.

Keep secrets, personal data, raw large logs, speculative claims, and full
internal addresses out of the journal. Use existing evidence paths rather than
copying outputs. If a safe write is blocked, report the missing entry instead
of inventing another state owner.

Write after a meaningful result and before a handoff or final response. It never
authorizes implementation, cleanup, Git actions, deployment, or external changes.
