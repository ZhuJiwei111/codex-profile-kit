# Memory Hygiene

Read this reference only after the user explicitly requests a memory audit,
cleanup, or update on the current execution host.

## Safe Sources

Use the smallest needed projection from the current host's:

- `~/.codex/memories/MEMORY.md`;
- `~/.codex/memories/memory_summary.md`;
- safe filenames and sizes under `rollout_summaries/`, `skills/`, and
  `extensions/`;
- user-approved ad-hoc notes.

Keep another host's memory outside the run. Do not read raw session
transcripts, rollout JSONL, `raw_memories.md`, auth, SQLite, attachments,
caches, logs, or credential-bearing state unless a higher-priority instruction
explicitly requires that exact source.

## Review Categories

- `keep`: durable, distinct, and likely to recur;
- `merge`: overlaps another topic but adds reusable knowledge;
- `compact`: useful but polluted by versions, PIDs, timestamps, old endpoints,
  or one-time live state;
- `delete`: user-approved removal or non-memory contamination;
- `provenance only`: retain rollout evidence but remove compact routing.

Age alone is not sufficient reason to delete a distinct topic. Label dynamic
facts historical unless freshly verified on the current host.

## Apply Through A New Note

After the user approves exact semantic changes, create one small file on the
current host:

`~/.codex/memories/extensions/ad_hoc/notes/<timestamp>-<short-slug>.md`

Record the approval, exact topics or preferences to add or change, intended
merged structure, provenance disposition, and safeguards against
reintroduction. Never edit or delete generated memory files or an existing
note.

Writing the note does not regenerate memory. Report it as submitted and
pending. End the current task if the user wants generation to run.

## Fresh-Task Verification

In a fresh task on the same host, verify generated-file timestamps, expected
headings and counts, approved removals, retained provenance and skills, and
absence of known contamination. Do not claim current operational facts from
memory without live verification.
