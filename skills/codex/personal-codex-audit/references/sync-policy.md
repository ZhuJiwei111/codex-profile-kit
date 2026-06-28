# Sync Policy

Use this policy when maintaining the user's portable Codex profile repository.

## Repository Boundary

- Default repository: `~/codex-profile-kit`.
- Default remote: `ZhuJiwei111/codex-profile-kit`.
- Visibility: private by default.
- Source of truth: active local `~/.codex` and `~/.agents` configuration.
- Repository role: portable, verified snapshot for sync and migration.

Do not turn the whole `~/.codex` directory into a Git repository. The profile kit
contains exported portable assets only.

## Included Assets

- Portable `rules/AGENTS.portable.md`.
- Non-system Codex skills under `skills/codex/`.
- Portable agent skills under `skills/agents/`.
- Native hook scripts and hook docs under `hooks/`.
- Hookify rules under `hooks/rules/`.
- `templates/` for target-machine local rendering.
- `scripts/sync.py`, README, install guide, connector checklist, manifest, and CI.

## Excluded Assets

Never export, commit, copy, print, or summarize secret values or runtime state:

- `auth.json`, tokens, cookies, passwords, private keys, `.netrc`, secret env files.
- `history.jsonl`, `session_index.jsonl`, sessions, attachments, logs, pasted files.
- SQLite state, WAL/SHM files, hook trusted hashes, approval history.
- Codex memories and rollout summaries unless the user separately approves a memory migration design.
- Plugin caches, connector OAuth state, app caches, model caches.
- Project trust lists, conda environments, package caches, datasets, model weights, project outputs.
- Generated tarballs in Git history.

## Commands

Run from `~/codex-profile-kit`:

```bash
python3 scripts/sync.py audit
python3 scripts/sync.py export --dry-run
python3 scripts/sync.py export
python3 scripts/sync.py verify
python3 scripts/sync.py push --confirm
python3 scripts/sync.py apply
python3 scripts/sync.py apply --confirm
```

`apply` is dry-run by default. Use `--confirm` only after the user approves the
reported overwrite set. The script must back up overwritten files first.

## Conflict Policy

Ask the user before changing or applying:

- `AGENTS.md` behavior rules, especially ask-first, language, long-job, sync, or safety rules.
- `config.toml`, project trust, hook trusted hashes, memories, connector state, or host-specific paths.
- Broad skill trigger descriptions or Hookify rules that may change everyday behavior.
- Any GitHub push, repository visibility change, release publication, or automation.

Low-risk updates may be prepared independently but should still be reported with
paths and verification evidence before completion.
