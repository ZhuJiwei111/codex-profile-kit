# Profile-Kit Sync Policy

Use this policy for the portable `codex-profile-kit`, not for general Git or
single-skill lifecycle work.

## Contents

- Repository and stage authorization
- Routine directional sync
- Preflight and portable asset boundaries
- Escalation triggers
- Export and apply
- Commit and push

## Repository Boundary

- Default repository: `~/codex-profile-kit`.
- Default remote: `ZhuJiwei111/codex-profile-kit`.
- Visibility may be public or private; confirm the actual visibility before
  publication and ensure the user's publication intent covers that exposure.
- Do not change repository visibility without separate explicit authority.
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
| `sync.py apply --confirm` | Writes active profile and backup | Explicit apply authority, or bounded inbound-sync intent whose plan remains inside the fast path |
| Commit | Changes local Git history | Explicit commit authority, or bounded outbound-sync intent whose diff remains inside the fast path |
| Push/publication | Changes external state | Explicit push/publication authority, or bounded outbound-sync intent for the existing remote, branch, and visibility |

Do not infer a later stage from a bare audit, export, apply, or comparison. An
explicit directional sync outcome is different: it authorizes its complete
bounded chain below, so do not ask again at each internal stage.

## Directional Intent

- **Sync to GitHub** means audit, export, exact-path commit, and push to the
  already configured remote and branch at its confirmed visibility.
- **Sync GitHub updates to this host** means fetch, non-conflicting integration,
  and confirmed apply of existing admitted portable targets with the standard
  timestamped backup.

These mappings do not authorize a pull request, repository or visibility
change, another host, conflict resolution with ambiguous ownership, credential
changes, or newly admitted content. A plan-only, audit-only, export-only, or
apply-only request remains limited to the named stage.

## Preflight

1. Lock direction, repository path, current host, actual repository visibility
   when publishing, and the applicable intent boundary.
2. Before Git network access, read the host connection contract routed by the
   active instructions and use its documented entrypoint. Do not probe direct,
   proxy, API, archive, or alternate transports first.
3. Run `git status --short` before a profile-kit write. Preserve existing user
   changes and stop if the intended command could absorb unrelated work.
4. Run `python3 scripts/sync.py audit` at the direction-specific point below and
   inspect the categorized diff.
5. Reconcile personal source-note presence and the third-party allowlist/content
   lock. Do not export host-only, unassessed, deferred, rejected, unlocked, or
   digest-drifted skills.

## Routine Fast Path

### Outbound

1. Preflight branch/upstream, author identity, worktree/index ownership, remote,
   visibility, and host network entrypoint. GitHub write authentication is not
   a prerequisite for creating the authorized local commit.
2. Run `sync.py audit`, then `sync.py export`. Export verifies the staged
   candidate, so do not run a redundant standalone `verify` while the exported
   state remains unchanged.
3. Inspect the exact portable diff and sensitive-path boundary. Stage only the
   approved paths and commit once. Do not make GitHub write authentication a
   prerequisite for the local commit. If a write-auth check is blocked,
   continue with the exact-path local Git commit.
4. Attempt ordinary `git push` through the host entrypoint after the commit. Do
   not make `gh` or GitHub connector authentication a prerequisite for `git
   push`. If either higher-level path is unavailable, fall back to ordinary
   `git push` through the host connection entrypoint. Report remote publication
   failure only when `git push` itself fails; do not describe a successful local
   commit as failed. When push succeeds, compare the resulting remote ref with
   `HEAD`.

### Inbound

1. Preflight worktree/index ownership and the host network entrypoint, then
   fetch and classify ancestry.
2. Fast-forward or create a non-conflicting merge as authorized. Stop on a
   merge conflict or ambiguous ownership.
3. Run `sync.py audit`, then `sync.py apply` once. The apply dry run verifies
   the repository and reports the exact target set.
4. When the target set contains only existing admitted portable targets, the
   inbound-sync intent authorizes `apply --confirm` with its timestamped backup.
   Run one post-apply audit and require zero drift.

Use one verification pass per unchanged state. Rerun only the check whose input
or artifact identity changed; do not stack `audit`, `verify`, export validation,
and apply validation merely for ceremony.

## Escalation Triggers

Leave the routine fast path and pause or invoke the owning workflow when any of
these appears:

- a new, removed, or renamed managed asset, including a skill, agent, hook, or
  lifecycle successor;
- changes to `AGENTS.md`, configuration/templates, the third-party lock, sync
  tooling, generated policy documents, trust-related state, host facts,
  memories, or excluded/sensitive paths;
- unrelated or ambiguous worktree state, a pre-populated index of uncertain
  ownership, a merge conflict, or ambiguous branch ancestry;
- a repository visibility change, different remote/branch/host, unconfirmed
  public exposure, or a pull-request/publication expansion;
- an admission/provenance conflict, changed Codex compatibility contract, a
  transport anomaly after using the documented host path, or a request to
  change credentials. Mere write-auth unavailability does not block an already
  authorized, verified local commit.

Ordinary content updates to existing admitted portable targets do not require a
whole-profile collector or a second authorization round merely because they
span more than one file.

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
git status --short
```

Export verifies its candidate. Review the actual diff and confirm that no
unrelated path was added. Do not stage, commit, or push as part of a bare
export request; bounded outbound-sync intent is the explicit exception.

Admission does not authorize export, and export does not grant admission. A
new portable vendor normally requires `admitted + complete + vendor`. A
documented pre-contract `legacy-exception` may preserve only its exact locked
snapshot and must fail before any update until provenance is completed.

## Apply

Run the dry run first:

```bash
python3 scripts/sync.py apply
```

Use `apply --confirm` after explicit approval, or directly under bounded
inbound-sync intent when the dry run lists only existing admitted portable
targets and the standard backup behavior. Re-check the backup path and run a
zero-drift audit after the write. `AGENTS.portable.md` and config templates
remain manual-review inputs, not automatic replacements for host-specific state.

## Commit And Push

The routine outbound fast path already exported and verified its candidate, so
do not call `sync.py push --confirm` after a completed export. Stage the exact
reviewed paths and use ordinary commit/push commands through the host network
entrypoint. Keep the local commit and remote push as separate outcomes: a
`gh` or connector authentication failure must fall back to ordinary `git push`
through the host connection entrypoint. Report remote publication failure only
when `git push` itself fails, and report a commit failure only when `git commit`
itself fails.

`sync.py push --confirm` remains a standalone all-in-one option only when no
separate export has run and the entire worktree diff is intentionally approved;
it exports, verifies, stages with `git add -A`, commits, and pushes. Do not use
it when the worktree contains unrelated or unapproved changes. Before either
push path, require all of the following:

1. Explicit commit and push authority, including bounded outbound-sync intent.
2. A clean or intentionally isolated diff containing only approved profile
   changes.
3. Verification success after the final export.
4. Confirmed intended remote and branch, actual repository visibility, and the
   user's authorization to publish the isolated diff at that exposure level.
5. For a public repository, confirmation that the isolated diff contains only
   approved portable assets and no excluded or sensitive state.

If those conditions are not all met, stop after local export and report the
remaining external action.
