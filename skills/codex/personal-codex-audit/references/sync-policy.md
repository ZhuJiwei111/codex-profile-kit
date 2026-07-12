# Profile-Kit Sync Policy

Use this policy for the portable `codex-profile-kit`, not for general Git or
single-skill lifecycle work.

## Contents

- Repository and stage authorization
- Preflight and portable asset boundaries
- Export and apply
- Commit and push

## Repository Boundary

- Default repository: `~/codex-profile-kit`.
- Default remote: `ZhuJiwei111/codex-profile-kit`.
- Visibility: private unless the user explicitly changes it.
- Export source of truth: active current-host `~/.codex` and `~/.agents`
  portable assets.
- Apply source of truth: the reviewed profile-kit snapshot and its approved
  target set.

Do not turn the complete Codex home into a Git repository.

## Stage Authorization

| Stage | State change | Required authority |
| --- | --- | --- |
| `sync.py audit` | No durable profile write | Read-only audit request |
| `sync.py export --dry-run` | No durable profile write | Read-only comparison request |
| `sync.py export` | Writes profile-kit | Explicit export/local sync intent |
| `sync.py verify` | No intended profile write | Normal verification after export or before apply |
| `sync.py apply` | Dry-run only | Read-only apply comparison |
| `sync.py apply --confirm` | Writes active profile and backup | Approval of the reported target set |
| Commit | Changes local Git history | Explicit commit authority |
| Push/publication | Changes external state | Explicit push/publication authority |

Do not infer a later stage from an earlier one. In particular, export does not
authorize commit or push.

## Preflight

1. Lock direction, repository path, current host, and furthest authorized
   stage.
2. Run `git status --short` before a profile-kit write. Preserve existing user
   changes and stop if the intended command could absorb unrelated work.
3. Run `python3 scripts/sync.py audit` and inspect the categorized diff.
4. Reconcile personal source-note presence and the third-party allowlist/content
   lock. Do not export host-only, unassessed, deferred, rejected, unlocked, or
   digest-drifted skills.
5. Pause when differences affect broad behavior, `AGENTS.md`, config templates,
   host facts, hooks, trust-related state, memories, or sensitive paths.

## Included Portable Assets

- `rules/AGENTS.portable.md`.
- Personal workflow skills and explicitly allowlisted portable skills.
- `THIRD_PARTY_SKILLS.lock.json`, which binds allowlisted vendor identities to
  reviewed source/license states and exact portable snapshot digests. It is
  profile policy and is not copied into the target Codex home.
- Agent skills under `skills/agents/`.
- Hook scripts, tests, safe hook documentation, and Hookify rules.
- Portable templates, connector checklist, manifest, sync tooling, and CI.
- Explicitly reviewed, public, non-secret MCP declarations in the manual config
  template; never authenticated runtime state.
- `HOST_LOCAL_TEMPLATE.md`, never the populated `HOST_LOCAL.md`.

## Excluded Assets

Never export, apply from a snapshot, commit, print, or summarize secret values
or runtime state:

- Auth/session/history files, tokens, cookies, passwords, private keys,
  `.netrc`, or secret environment files.
- SQLite state, attachments, logs, pasted files, memories, or rollout summaries.
- Hook trust hashes, approval history, project trust, connector OAuth state, or
  plugin/app/model caches.
- MCP command lines, arguments, environment entries, bearer-token fields,
  header material, OAuth/login state, runtime health, or tool output.
- Conda environments, package caches, datasets, model weights, project outputs,
  or generated tarballs in Git history.
- Non-personal installed suites unless explicitly allowlisted.
- Host-only, unassessed, deferred, rejected, unlocked, or locally drifted
  third-party skills.

## Export

After explicit export authority:

```bash
python3 scripts/sync.py export
python3 scripts/sync.py verify
git status --short
```

Review the actual diff and confirm that no unrelated path was added. Do not
stage, commit, or push as part of ordinary export.

Admission does not authorize export, and export does not grant admission. A
new portable vendor normally requires `admitted + complete + vendor`. A
documented pre-contract `legacy-exception` may preserve only its exact locked
snapshot and must fail before any update until provenance is completed.

## Apply

Run the dry run first:

```bash
python3 scripts/sync.py apply
```

Use `apply --confirm` only after the user approves the listed targets and
backup behavior. Re-check the backup path and verify the active files after the
write. `AGENTS.portable.md` and config templates remain manual-review inputs,
not automatic replacements for host-specific state.

## Commit And Push

`sync.py push --confirm` exports, verifies, stages with `git add -A`, commits,
and pushes. Do not use it when the worktree contains unrelated or unapproved
changes. Before using it, require all of the following:

1. Explicit commit and push authority.
2. A clean or intentionally isolated diff containing only approved profile
   changes.
3. Verification success after the final export.
4. Confirmed private remote and intended branch.

If those conditions are not all met, stop after local export and report the
remaining external action.
