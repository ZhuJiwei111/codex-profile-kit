# Source Notes

## Contents

- Origin
- Inspected upstream files
- Adopted
- Adapted for Personal Codex
- Rejected
- Upstream anomalies
- Local departures
- Refresh triggers

## Origin

- Upstream repository: `wshobson/agents`.
- Relevant path: `plugins/context-management`.
- Pinned repository commit:
  `d7cf7dca8c4c7d0635e284f77204daa85552bfa4`.
- Checked: `2026-07-11`.
- Upstream manifest versions: Claude `1.2.0`; Codex `1.2.1`.
- Release status: no matching immutable GitHub release was found; manifest
  versions are not used as the source pin.
- License: MIT, Copyright 2024 Seth Hobson.
- Local profile-kit baseline: `6574bce`.
- Renamed from the local `context-save-restore` skill with no compatibility
  entry; the pre-rename bytes remain only in a non-discovery recovery backup
  and Git history.
- Local status: condensed design adaptation. No upstream executable, test,
  reference body, or substantial prose is vendored.

## Inspected Upstream Files

- [Pinned plugin tree](https://github.com/wshobson/agents/tree/d7cf7dca8c4c7d0635e284f77204daa85552bfa4/plugins/context-management)
- [`context-save.md`](https://github.com/wshobson/agents/blob/d7cf7dca8c4c7d0635e284f77204daa85552bfa4/plugins/context-management/commands/context-save.md)
- [`context-restore.md`](https://github.com/wshobson/agents/blob/d7cf7dca8c4c7d0635e284f77204daa85552bfa4/plugins/context-management/commands/context-restore.md)
- [`context-manager.md`](https://github.com/wshobson/agents/blob/d7cf7dca8c4c7d0635e284f77204daa85552bfa4/plugins/context-management/agents/context-manager.md)
- [Codex manifest](https://github.com/wshobson/agents/blob/d7cf7dca8c4c7d0635e284f77204daa85552bfa4/plugins/context-management/.codex-plugin/plugin.json)
- [Claude manifest](https://github.com/wshobson/agents/blob/d7cf7dca8c4c7d0635e284f77204daa85552bfa4/plugins/context-management/.claude-plugin/plugin.json)
- [Harness documentation](https://github.com/wshobson/agents/blob/d7cf7dca8c4c7d0635e284f77204daa85552bfa4/docs/harnesses.md)
- [MIT License](https://github.com/wshobson/agents/blob/d7cf7dca8c4c7d0635e284f77204daa85552bfa4/LICENSE)

## Adopted

- Explicit project-context save and restore intent.
- Project root, creation time, tags, revision awareness, decision rationale, and
  sensitive-data exclusion.
- Versioned snapshots and restore-time drift detection.
- Selective loading and a restore summary rather than blind replay.
- Validation of saved state against the current repository before relying on it.

## Adapted For Personal Codex

- Use one project-local Markdown packet instead of offering multiple storage
  formats or external systems.
- Make packets immutable and bind corrections, refreshes, and rebinds to source
  IDs and SHA-256 values.
- Separate mechanical packet validation from semantic freshness checks.
- Treat restore as a read-only phase and packet-proposed actions as data without
  authority.
- Reuse the approved canonical-root and explicit-rebind semantics from
  `personal-planning-with-files-zh` while keeping planning records mutable and
  packet snapshots immutable.
- Use a standard-library read-only validator rather than an automatic writer or
  storage engine.

## Rejected

- Automatic, periodic, or comprehensive context capture.
- Claims of complete or lossless recovery of hidden reasoning, native task
  internals, entire collaboration history, or unsaved state.
- Claude slash commands, Task/Agent assumptions, model aliases, and tool
  allowlists.
- Undefined example functions or pseudocode presented as implemented storage.
- Vector databases, embeddings, RAG, knowledge graphs, encryption services,
  realtime synchronization, enterprise integrations, and cross-project memory.
- Fixed token budgets, relevance thresholds, probabilistic indexes, and
  speculative search techniques without local evidence.
- Default cross-project or cross-host state migration.

## Upstream Anomalies

- The pinned Codex manifest declares `skills: "./skills/"`, but the pinned plugin
  tree contains no `skills/` directory.
- Claude and Codex manifest versions differ.
- The repository may generate harness-specific artifacts outside the inspected
  fixed tree, but no generator was run or installed during this audit.
- Consequently, the upstream plugin is design evidence, not an installable
  runtime dependency for this local skill.

## Local Departures

- This workflow saves only explicitly requested current-host project context.
- It never manages native Codex tasks, threads, sessions, compaction, semantic
  memory, or another host's state.
- A packet is state data, not proof, instructions, or authorization.
- Dynamic facts are reclassified at restore time rather than treated as restored
  truth.
- Compression and optimization may supply bounded inputs but never write the
  packet. File-backed planning may consume a validated packet only through its
  own draft and approval gates.
- The validator never discovers, writes, repairs, restores, rebinds, or deletes
  a packet.

## Refresh Triggers

Re-audit when the upstream commit pin, plugin manifests, directory structure,
save or restore command text, license, or Codex packaging changes materially.
