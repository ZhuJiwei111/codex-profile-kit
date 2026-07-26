---
name: personal-profile-sync
description: Manual only. Use only when the user explicitly invokes this skill to preview, apply, or check the portable Codex profile, update the local portable repository from GitHub before applying it, or commit and non-force push an explicitly named portable-profile change.
---

# Personal Profile Sync

Treat this Git working tree as the only editable portable source and the
current host's official `$CODEX_HOME` as a deployment target. Never export
active profile state back into the repository.

## Choose The Explicit Intent

- `preview`, `apply`, or `check`: run `scripts/profile_sync.py` with the
  `codex-tools` Python recorded in `HOST_LOCAL.md`.
- update from GitHub: inspect local state, fetch, and accept only a selected
  non-conflicting update before preview/apply.
- submit or sync to GitHub: validate and inspect the exact diff, stage only
  task-owned paths, create one factual commit, and non-force push. Do not create
  a PR unless separately requested.

The sync script performs no Git operation. Calling `apply` is authorization for
the scoped local profile write; it is not push authority.

## Apply From A Reviewed Commit

For new portable changes, validate source and skills, run focused checks,
preview the exact diff, inspect it, stage exact paths, and create a local
factual commit before deployment. Reusing an existing reviewed commit does not
create an empty commit.

`apply` owns only the manifest paths and the configured leaf keys. It must show
the resolved target, create a timestamped exact-target backup when changes
exist, use the official config writer, and finish with `check`. It does not
manage credentials, sessions, trust, caches, plugins, host facts, connection
contracts, or unlisted configuration.

When hook definitions change, keep any runner still loaded by the current task.
Use a fresh task to review `/hooks` trust and dispatch before retiring that old
runner. Report the backup path, commit, checks, unrun work, and remaining fresh
task action.
