---
name: personal-project-journal
description: Use by default when a durable project event occurs in a Git repository that already has .agent/JOURNAL.md, and during an authorized repository-write task when no journal exists to initialize a trackable monthly project audit journal; keep human-readable event history separate from active planning and durable project authority.
---

# Personal Project Journal

Maintain a human-readable history of events that can affect future project work
without turning it into current task state, a decision authority, or a
transcript.

## Resolve The Journal Owner

Locate the Git root and read applicable repository instructions. Update the
primary repository that received the durable event. Update another repository
only when it received its own durable event or actual write; do not journal an
incidental dependency. The main process owns journal writes. Subagents and
bounded workers return evidence instead of editing a journal.

When `.agent/JOURNAL.md` exists, read its instructions, index, and enough recent
entries to understand the local format. Follow narrower repository rules and
preserve an existing single-file or otherwise different layout. Do not migrate,
normalize, or backfill an existing journal implicitly.

## Initialize Only With Existing Write Authority

When a Git repository has no journal, initialize it only during a task already
authorized to write that repository and record that task's durable event. Do
not initialize a journal during a read-only task, in a non-Git or projectless
directory, or merely because the repository was inspected. If an existing
`.agent` layout directly conflicts with the target files, preserve it and
report the conflict. Do not edit `.gitignore` or replace adjacent files without
separate authority.

For a new journal, read and instantiate the bundled assets:

- `assets/journal-index.md` as `.agent/JOURNAL.md`;
- `assets/journal-readme.md` as `.agent/README.md`;
- `assets/journal-month.md` as `.agent/journal/YYYY-MM.md`.

Replace the month placeholders with the task's local calendar month. Keep the
files trackable, but do not stage, commit, or push them without matching Git
authority. Do not reconstruct entries for work that predates initialization.

## Record Durable Project Events

Write one entry when work produces at least one durable event:

- an actual repository-content change;
- a project-level user decision, prohibition, or scope contract;
- a confirmed root cause, important blocker, or expensive failure worth
  preventing later;
- a consequential external action, handoff, or final outcome.

Ordinary explanation, browsing, repeated status, and verification that changes
no conclusion do not need an entry. Once a journal exists, its maintenance is a
narrow standing write exception for a qualifying event even during an otherwise
read-only task.

Classify detail by audit importance:

- `high`: user authority or prohibition, scope or contract change, critical
  gate, failure root cause, costly pitfall, consequential external action,
  handoff, or final outcome; retain the important rationale and impact;
- `medium`: material implementation, diagnosis, phase advance, or changed risk;
  retain the consequential delta and actual evidence when useful;
- `routine`: ordinary durable maintenance or implementation; keep one to three
  factual sentences.

Keep the stable heading and write the body in the natural shape of the event:

```markdown
## <ISO-8601 timestamp with offset> · <high|medium|routine> · <topic>

<concise request and outcome summary>

- **改动**：<include only when useful>
- **证据**：<include only evidence already gathered and worth retaining>
- **影响 / 后续**：<include only when consequential>
```

Labels are optional. Do not fill unused fields or run extra checks merely to
complete an entry. Write after relevant checks and before the final response,
handoff, stop, compaction, or archive. Record only Git and external state
already observed. Never predict a future commit or push merely to make the
entry look final, and do not create a second entry solely to report an ordinary
commit or push; Git owns that history.

## Preserve Audit History

For the managed monthly layout, create a new month file when needed, add its
link immediately below `<!-- journal-months -->`, and insert new entries
immediately below `<!-- journal-entries -->`. Keep both lists newest first.
Preserve the meaning of older entries. Correct a material fact, decision, or
conclusion with a new entry that identifies the earlier timestamp and topic;
minor spelling, punctuation, or formatting fixes that do not change meaning may
be edited directly.

Read the target and append through its existing insertion point. If the layout
or patch operation actually prevents a safe update, leave the journal untouched
and report the missing entry instead of stacking fallback write paths.

Never record credentials, tokens, private keys, personal data, full internal
addresses, secret-bearing commands, raw large logs, or unsupported inference.
Summarize sensitive evidence and point only to an already-safe canonical owner.

## Keep State Owners Separate

JOURNAL owns chronological event history. An active file-backed plan owns the
current goal, phase, findings, blocker, and next action. Durable
project documents own binding decisions and contracts; Git, tests, receipts,
and live checks remain evidence. Journal only the task delta and link to those
owners instead of copying their full contents.

This skill authorizes only journal-owned writes described above. It never
authorizes implementation, cleanup, staging, commits, pushes, publication,
deployment, monitoring, or another external action.
