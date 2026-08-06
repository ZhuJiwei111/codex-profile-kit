---
name: personal-project-journal
description: Use by default for every substantive task in a Git repository that already has .agent/JOURNAL.md, and during an authorized repository-write task when no journal exists to initialize a trackable monthly project audit journal; keep human-readable history separate from active planning and durable project authority.
---

# Personal Project Journal

Maintain a human-readable chronological audit trail without turning it into
current task state, a decision authority, or a transcript.

## Resolve The Journal Owner

Locate the Git root and read applicable repository instructions. Update the
primary repository and every other repository that received substantive work
or writes; do not journal repositories that were only incidental dependencies.
The main process owns journal writes. Subagents and bounded workers return
evidence to the main process instead of editing a journal.

When `.agent/JOURNAL.md` exists, read its instructions, index, and enough recent
entries to understand the local format. Follow narrower repository rules and
preserve an existing single-file or otherwise different layout. Do not migrate,
normalize, or backfill an existing journal implicitly.

## Initialize Only With Existing Write Authority

When a Git repository has no journal, initialize it only during a task that is
already authorized to write that repository. Do not initialize a journal during
a read-only task, in a non-Git or projectless directory, or merely because the
repository was inspected.

Before initialization, verify that `.agent` and the target files are not
symlinks and that the proposed paths are not ignored. If an existing `.agent`
layout is incompatible, any target is a symlink, or Git ignore policy excludes
the journal, skip initialization and report why. Do not edit `.gitignore` or
replace adjacent files without separate authority.

For a new journal, read and instantiate the bundled assets:

- `assets/journal-index.md` as `.agent/JOURNAL.md`;
- `assets/journal-readme.md` as `.agent/README.md`;
- `assets/journal-month.md` as `.agent/journal/YYYY-MM.md`.

Replace the month placeholders with the task's local calendar month. Keep the
files trackable, but do not stage, commit, or push them without matching Git
authority. Do not reconstruct entries for work that predates initialization.

## Record Every Substantive Task

Write one entry for each substantive user request or continuation that produces
a result, decision, state change, verification, blocker, external observation,
or handoff. Once a journal exists, its maintenance is a narrow standing write
exception even for an otherwise read-only substantive task. Simple
acknowledgements, greetings, clarifications with no result, and repeated status
with no new evidence do not need an entry.

Classify detail by audit importance:

- `high`: user authority or prohibition, scope or contract change, critical
  gate, failure root cause, costly pitfall, external action, handoff, or final
  outcome; retain rationale, evidence, and impact;
- `medium`: material implementation, diagnosis, phase advance, or changed risk;
  retain the consequential delta and evidence anchors;
- `routine`: ordinary substantive analysis, verification, or maintenance; keep
  a short factual summary.

Use this shape, with concise `无` values when a field is inapplicable:

```markdown
## <ISO-8601 timestamp with offset> · <high|medium|routine> · <topic>

- **目标**：<request or purpose>
- **结果**：<outcome or decision>
- **改动**：<task changes, explicitly separating journal maintenance>
- **验证 / 证据**：<fresh checks or evidence anchors>
- **决定 / 风险**：<authority, supersession, caveat, or remaining risk>
- **状态 / 后续**：<observed state and concrete continuation, if any>
```

Write after the task's relevant fresh checks and before the final response,
handoff, stop, compaction, or archive. Record only Git and external state
observed before the journal edit. Never predict a future commit or push merely
to make the entry look final.

## Preserve Audit History

For the managed monthly layout, create a new month file when needed, add its
link immediately below `<!-- journal-months -->`, and insert new entries
immediately below `<!-- journal-entries -->`. Keep both lists newest first.
Modify no older entry bytes. Correct a material historical error with a new
entry that identifies the earlier timestamp and topic; do not silently rewrite
history.

Read the latest file again immediately before patching. If concurrent edits,
conflict markers, or an unrecognized insertion boundary prevent an exact
append-only change, leave the journal untouched and report the missing entry.
Do not let journal failure erase or misrepresent the task's actual result.

Never record credentials, tokens, private keys, personal data, full internal
addresses, secret-bearing commands, raw large logs, or unsupported inference.
Summarize sensitive evidence and point only to an already-safe canonical owner.

## Keep State Owners Separate

JOURNAL owns chronological audit history. An active file-backed plan owns the
current goal, phase, findings, progress, blocker, and next action. Durable
project documents own binding decisions and contracts; Git, tests, receipts,
and live checks remain evidence. Journal only the task delta and link to those
owners instead of copying their full contents.

This skill authorizes only journal-owned writes described above. It never
authorizes implementation, cleanup, staging, commits, pushes, publication,
deployment, monitoring, or another external action.
