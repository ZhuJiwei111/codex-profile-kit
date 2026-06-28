---
name: context-save-restore
description: Use when explicitly saving, restoring, or handing off project context across Codex sessions, especially when a user asks for context save, context restore, resume packets, or durable session state.
metadata:
  sources:
    - https://github.com/wshobson/agents/tree/main/plugins/context-management
---

# Context Save Restore

## Scope

This skill adapts the upstream `context-management` plugin to a Codex-native, file-backed workflow. It covers explicit context lifecycle operations: save current project state, restore a prior state packet, or prepare a handoff.

## Boundaries

Use these instead when appropriate:

- `context-compression`: compressing a long active conversation.
- `context-optimization`: reducing token budget or improving retrieval strategy.
- `filesystem-context`: designing file-backed scratchpads for ongoing work.
- `memory-systems`: persistent semantic memory architecture.
- `planning-with-files-zh`: active multi-step task planning with `task_plan.md`, `findings.md`, `progress.md`.

## Save Packet

Create a compact Markdown file under a project-local directory such as `.codex/context/`:

```markdown
---
type: context-save
created_at: YYYY-MM-DDTHH:MM:SSZ
project_root: /absolute/path
tags: []
---

# Context Save

## Goal

## Current State

## Important Files

## Decisions

## Verification

## Open Questions

## Resume Instructions
```

Keep it factual and auditable. Do not copy secrets, credentials, private keys, cookies, tokens, or full logs containing sensitive values.

## Restore Procedure

1. Locate the requested context packet.
2. Read it before touching code.
3. Verify the current working tree with `git status --short` if inside a repo.
4. Reconcile stale paths or changed files before acting.
5. State what was restored and what remains uncertain.

## Handoff Procedure

When preparing another agent or future session:

- Write the current objective and exact next action.
- List changed files and verification results.
- Include blockers and assumptions.
- Prefer links to local files over pasted large content.

## Common Mistakes

| Mistake | Correction |
|---|---|
| Saving everything | Save only what affects continuation. |
| Treating restored context as truth | Verify against the current filesystem and git state. |
| Mixing context packets with active plans | Use this for session lifecycle; use planning skills for task execution. |
| Copying secrets into context | Record only the category/path and redact values. |
