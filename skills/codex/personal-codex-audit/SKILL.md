---
name: personal-codex-audit
description: "Manual only. Use for one explicit current-host portable-profile intent: read-only audit, export active managed assets to the local codex-profile-kit repository, export and publish them to GitHub, or fetch a reviewed GitHub revision and apply its managed assets to the active profile."
---

# Personal Codex Audit

Run only after the user selects one exact intent. Do not infer writes, network
access, Git actions, or active-profile application from another intent.

The four intents are:

- `audit`: compare the current host's managed active profile and selected
  repository read-only;
- `export repo`: conservatively overlay present managed active assets onto the
  local repository and stop before Git staging or publication;
- `sync GitHub`: export the managed active assets, verify the exact repository
  candidate, then commit and non-force push it through the Git owner; or
- `from GitHub apply active`: obtain one reviewed exact GitHub revision, apply
  its managed assets to this host, and verify the result.

Use the repository's `scripts/sync.py` with its required Python 3.11+
interpreter. Keep that script as the deterministic transfer owner; do not build
a second inventory collector.

## Keep The Managed Boundary Exact

Manage only:

- `rules/AGENTS.portable.md` as the complete portable active `AGENTS.md`;
- Codex skill directories named `personal-*`; and
- another target only when `scripts/sync.py` explicitly inventories it and the
  current request includes that target.

Exclude non-personal skills, `HOST_LOCAL.md`, `config.toml`, credentials,
auth/session state, connection state, caches, logs, memories, histories,
attachments, other runtime state, and custom agent profiles. Preserve excluded
and unrelated repository/profile state.

One narrow lifecycle exception applies: confirmed apply may back up and remove
only the exact retired active-profile paths hard-coded by `scripts/sync.py` and
listed in `MIGRATION_MANIFEST.md`, including the two retired custom-agent files.
Those tombstones are not exported, do not make custom agents managed content,
and do not authorize deletion by ordinary repository absence. If a preview
includes any other excluded or unrequested target, stop before mutation.

The current host and explicitly selected repository/worktree bound the task.
Do not inspect or synchronize another host by implication.

Export is intentionally not a destructive mirror. An active personal skill or
explicit hook script can add or replace its repository counterpart, but absence
from the active profile does not delete a repo-only entry. The repository owns
`templates/hooks.json.template`; export does not reverse-render active
`~/.codex/hooks.json` into that template. Audit may therefore still report
inbound drift after export when the repository intentionally contains an entry
that this host has not applied.

## Audit

1. Confirm the repository/worktree, current host, managed target set, and
   exclusions.
2. Run `scripts/sync.py audit` read-only and inspect categorized drift.
3. Report managed differences, excluded state, unknowns, and the exact later
   intent required for any change. Do not export, apply, fetch, stage, commit,
   or push.

## Export Repo

1. Inspect repository root, branch, index, dirty state, overlapping user work,
   and managed ownership.
2. Run audit, then one `scripts/sync.py export`. Inspect the exact reported
   paths and complete Git diff for containment, symlinks, secrets, host facts,
   excluded surfaces, and unrelated changes.
3. Use `personal-risk-verification` for a fresh semantic final judgment over
   the resulting repository candidate.
4. Stop with the local repository diff. Export authority does not stage,
   commit, push, create a PR, or alter the active profile.

## Sync GitHub

This intent explicitly authorizes the outbound local export plus one exact
commit and non-force push; it does not authorize a pull request.

1. Follow the `export repo` audit, export, complete-diff inspection, and
   semantic final-verification path on the unchanged candidate.
2. Resolve the exact task-owned paths, branch, remote, source ref, and
   destination ref. Preserve unrelated repository and index state.
3. Hand the verified candidate to `personal-branch-finish` in its
   `commit + push` mode. That skill owns exact staging, the factual commit, and
   direct non-force push. `scripts/sync.py` never performs Git actions.
4. Report the local commit and remote ref actually confirmed. Do not create or
   amend another commit, create a pull request, or install a publication
   dependency. Stop on ownership ambiguity, hook mutation, non-fast-forward,
   authentication failure, or remote/ref mismatch.

## From GitHub Apply Active

1. Inspect repository/worktree ownership, branch, index, dirty state, remote,
   and exact source ref. Fetch only the selected remote evidence and resolve the
   exact commit. Integrate it only by the repository's permitted conflict-free
   path; stop on divergence, conflict, ambiguous ancestry, or overlapping dirty
   state rather than merging or rebasing by guesswork.
2. Review the selected revision and run `scripts/sync.py audit`, followed by one
   exact `scripts/sync.py apply` dry run. Confirm that the preview touches only
   managed requested targets and leaves exclusions unchanged.
3. Immediately before confirmation, re-identify the repository revision,
   active candidate, and target list. If any changed, repeat the preview.
   Otherwise run `scripts/sync.py apply --confirm` and retain its timestamped
   backup when changes occur.
4. Run a post-apply audit and inspect the resulting active managed assets. Use
   `personal-risk-verification` for one fresh semantic final judgment covering
   the applied state and exclusions.

If the preview retires a hook command used by the current task's already loaded
hook definition, finish all other tool-dependent work before confirmed apply
and bind the post-apply audit to one fresh bounded worker/task. The current task
may keep invoking the cached command after its file is removed. Do not keep a
compatibility shim as final state; if recovery needs one, make it exact and
temporary, then remove it before the fresh zero-drift audit.

If apply fails, stop and report whether transactional rollback restored the
previous state and where the recovery backup remains. Do not improvise a
broader overwrite. An empty preview is a no-op.

## Stop Boundaries

Stop before mutation for unclear ownership, unsafe symlinks, path escape,
secret-bearing content, excluded targets, changing previews, ambiguous Git
ancestry, or a required credential/user decision. Never equate local export or
verification with GitHub synchronization, and never equate a pushed repository
with application to the active profile.

Report the selected intent, exact host/repository/revision, managed paths,
commands and outcomes, changes actually made, final semantic evidence, checks
not run, recovery path, and remaining risk.

See [source notes](references/source-notes.md) only when maintaining this
skill's transfer boundary.
