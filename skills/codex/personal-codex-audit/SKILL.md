---
name: personal-codex-audit
description: "Audit, summarize, export, migrate, compare, and synchronize the user's reusable Codex profile: server-level AGENTS.md preferences, personal skills, Hookify/native hooks, profile-kit GitHub synchronization, and reusable workflow memory signals. Use when the user asks to summarize, audit, refresh, migrate, sync, push, pull, apply, compare, or improve Codex preferences, skills, hooks, Hookify rules, or the portable codex-profile-kit workflow."
---

# Personal Codex Audit

## Overview

Audit the current reusable Codex working profile and, when explicitly requested,
help export or synchronize the portable `codex-profile-kit`. Treat plain audits
as read-only. Treat export, apply, push, pull, or sync as configuration changes
that require explicit user intent and verification.

## Workflow

1. Start read-only. Do not edit `AGENTS.md`, skills, hooks, memory, config, migration kits, profile-kit repositories, or generated reports unless the user separately asks for a concrete modification.
2. Read `references/source-policy.md` before gathering evidence. Follow its allowed sources, exclusions, and memory-filtering rules.
3. Run `scripts/collect_codex_profile.py --home "$HOME"` when the local filesystem is available. Use the JSON as the current-state inventory for preferences, skills, hooks, and headings.
4. Search memory lightly only for reusable, cross-task Codex workflow preferences. Do not summarize project-specific, platform-specific, experiment-specific, remote-host-specific, or task-log memory by default.
5. Use script-derived counts for skills, Hookify rules, native hooks, and headings. Reconcile manual groupings against those counts before reporting.
6. Write a concise Chinese report grounded in current files and any reusable memory signals. Clearly separate observed state from suggestions.

## Sync Workflow

Use this only when the user explicitly asks to export, sync, push, pull, apply,
or maintain the Codex profile kit.

1. Read `references/sync-policy.md`.
2. Treat active local config as source of truth for export. The default repo path is `~/codex-profile-kit`.
3. Prefer `python3 ~/codex-profile-kit/scripts/sync.py audit` before deciding whether to export, push, or apply.
4. For export/push from this machine, run `sync.py export`, then `sync.py verify`, then inspect `git status --short`. Push only after explicit user approval for GitHub publication.
5. For apply from a repo to an active machine, run `sync.py apply` first. It is dry-run by default. Use `sync.py apply --confirm` only after the user approves the reported overwrite set.
6. Pause for user judgment when differences affect `AGENTS.md`, `config.toml`, host facts, credentials, sensitive paths, memories, project trust, hook state, or any broad behavior rule.
7. Never copy auth/session/cache/SQLite/memory/plugin state into the kit or from the kit into active config.

## Report Format

Use these Chinese section labels unless the user asks for another format:

- `当前偏好`: durable behavior rules visible in `AGENTS.md`, grouped by workflow area.
- `当前 skills`: active personal/custom skills, their triggers, and any overlap or broad trigger risk.
- `当前 hooks`: Hookify and native hooks, including enabled state and action type when visible.
- `可共用记忆信号`: only reusable cross-task preferences or workflow lessons, with source caveats.
- `同步状态`: profile-kit repo state, export/apply direction, dry-run diff, verification status, and GitHub publication state when sync was requested.
- `漂移/冲突/过时风险`: stale wording, overlapping rules, overly broad triggers, missing validation, or host-specific assumptions.
- `需要你批准的建议`: concrete next edits or cleanup steps that require user approval.

## Safety Rules

- Never print secrets, credentials, private keys, cookies, tokens, auth files, raw session logs, or long memory extracts.
- Do not read `auth.json`, `history.jsonl`, `session_index.jsonl`, SQLite files, cache/plugin-cache directories, attachments, or session transcript directories.
- If a useful finding would require reading sensitive or high-noise sources, state the limitation and ask for explicit approval.
- Prefer direct current files over stale memory. When memory is used, label it as memory-derived and possibly stale.
- Keep recommendations narrow: update global/user-level configuration only when the user explicitly requests that next step.
- Keep GitHub repositories private by default for personal Codex profile synchronization. Do not publish or push until the user explicitly authorizes it.

## Resources

- `scripts/collect_codex_profile.py`: Collect a safe JSON inventory from current files. It writes only to stdout.
- `references/source-policy.md`: Source allowlist, default exclusions, and memory-filtering policy.
- `references/sync-policy.md`: Profile-kit repository, export/apply, GitHub sync, and conflict policy.

Use the script output as evidence, then apply judgment for the final Chinese summary.
