---
name: personal-context-compression
description: Use when a long session needs compact continuation, durable handoff, context compaction, or a summary that preserves files, decisions, risks, current state, and next actions.
---

# Personal Context Compression

Compress for tokens-per-task, not tokens-per-request. A bad summary that forces
re-reading files costs more than it saves.

## Summary Schema

Use structured sections:

- Goal and user constraints.
- Files read, modified, created, and why; keep full paths and identifiers.
- Decisions made and rationale.
- Current state, verification results, and failures.
- Risks, blockers, and next actions.

## Rules

- Prefer anchored iterative summaries: summarize only new material and merge into
  the existing summary.
- Preserve error messages, function names, config keys, commands, and paths
  verbatim when they matter.
- Do not compress tool schemas, API shapes, critical code snippets, secrets, or
  unresolved debugging evidence.
- Validate with probes: “what changed?”, “what failed?”, “what decision was
  made?”, “what is next?”

## Long-Run Handoff

For jobs expected to run longer than 10 minutes, preserve the detached launcher
(`tmux` session or `nohup` command), cwd, environment, key config, log and output
paths, estimated completion time, one-shot status-check command, and artifacts to
analyze after completion.

## Anti-Patterns

- “Updated config” without the file path.
- Dropping early user constraints.
- Treating readable prose as proof that technical state was preserved.
