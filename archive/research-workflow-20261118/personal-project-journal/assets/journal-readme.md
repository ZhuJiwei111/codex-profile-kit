# `.agent/` project audit journal

JOURNAL records what changed, why it matters, and the evidence or remaining
owner. It is event history, not proof of current state, a transcript, or a plan.

## Layout

- `JOURNAL.md` indexes monthly journals, newest first.
- `journal/YYYY-MM.md` keeps entries below `<!-- journal-entries -->`, newest first.
- Preserve existing project-specific files, work lines, statuses, and lifecycle rules.

## Events

Record a material change, decision, cause, blocker, handoff, or outcome.
Skip routine discussion, browsing, and unchanged verification. Keep one coherent
task entry, updating an active entry at real phase changes. Correct frozen facts
with a dated note or new entry rather than silently changing their meaning.

Use `high` for decisions, scope, costly failures, and important handoffs;
`medium` for implementation or changed risk; `routine` for ordinary durable
maintenance. Completion alone is never a reason to compress an important result.
A routine event needs only one to three factual sentences, not a filled form.

## Ownership and evidence

Plans own current task state, cards own experiment evidence, and project docs
own binding decisions. Link to those owners; do not synchronize copies here.
Distinguish saved, checked, committed, pushed, and actually running states.
Use local time with an offset. Keep only evidence already observed.

Preserve privacy and secrets. Write atomically, read back the changed anchor,
and report a blocked journal write. Tracking, staging, commit, push, and other
external actions require their own authority; preserve existing ignore policy.
