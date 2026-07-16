# Profile-Kit Sync Policy

Use this policy for the portable `codex-profile-kit`, not for general Git or
single-skill lifecycle work.

## Contents

- Repository and stage authorization
- Routine directional sync
- Preflight and portable asset boundaries
- Escalation triggers
- Export and apply
- Publication handoff

## Repository Boundary

- Default repository: `~/codex-profile-kit`.
- Default remote: `ZhuJiwei111/codex-profile-kit`.
- Visibility may be public or private. Before publication, confirm the actual
  visibility and authorization to publish the isolated diff at that visibility.
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
| Publication handoff | No Git mutation by this workflow | Bounded outbound-sync intent plus `personal-risk-verification: supported` |

Do not infer a later stage from a bare audit, export, apply, or comparison. An
explicit directional sync outcome is different: it authorizes its complete
bounded chain below, so do not ask again at each internal stage.

## Directional Intent

- **Sync to GitHub** means audit, export, final local verification, and a
  bounded handoff to `github:yeet`, which owns the complete branch, commit,
  push, and draft pull-request flow.
- **Sync GitHub updates to this host** means fetch, non-conflicting integration,
  and confirmed apply of existing admitted portable targets with the standard
  timestamped backup.

These mappings do not authorize a ready-for-review transition, merge,
repository or visibility change, another host, conflict resolution with
ambiguous ownership, credential changes, or newly admitted content. Outbound
sync authorizes only the default draft pull request owned by `github:yeet`. A
plan-only, audit-only, export-only, or apply-only request remains limited to the
named stage.

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
   visibility, and host network entrypoint. Network, proxy, and connection
   evidence selects only the transport path; it grants no publication,
   credential, installation, launch, or verdict authority.
2. Run `sync.py audit`, then `sync.py export`. Export verifies the staged
   candidate, so do not run a redundant standalone `verify` while the exported
   state remains unchanged.
3. Inspect the exact portable diff and sensitive-path boundary, then obtain a
   `personal-risk-verification: supported` verdict for the unchanged candidate.
   The profile executor must not stage, commit, or push it.
4. Hand the complete publication flow to `github:yeet` with the schema below.
   That owner starts from the uncommitted candidate and owns branch setup,
   staging, commit, push, and draft pull-request creation.

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

Emit a visible checkpoint after preflight that names the locked candidate and
the next incomplete stage. If a command or worker hits a deterministic blocker,
report the blocker before another attempt; do not accumulate silent retries or
serial handoffs around the same unchanged failure.

Run Python-based audit, export, and validation commands with
`PYTHONDONTWRITEBYTECODE=1` so they do not create `__pycache__`. If an ignored
`__pycache__` or `.pyc` still appears, classify it once as a transient validation
artifact. It does not reopen semantic review or justify repeating completed
gates. Any removal remains governed by the active cleanup and temporary-work
authorization boundary.

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
  public exposure, or a ready-for-review, merge, or publication expansion beyond
  the bounded draft-PR handoff;
- an admission/provenance conflict, changed Codex compatibility contract, a
  transport anomaly after using the documented host path, or a request to
  change credentials. Missing publication helpers do not authorize installation.

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
unrelated path was added. Do not stage, commit, or push from this workflow.
Bounded outbound-sync intent authorizes only the publication handoff after the
final supported verdict.

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

## Publication Handoff

Do not call `sync.py push --confirm` after a completed export—or at any other
stage. The legacy `sync.py push` parser entry is fail-closed compatibility only:
with or without `--confirm`, it exits nonzero before export, status inspection,
staging, commit, or push. It directs the operator to `audit` → `export` →
`inspect` → `personal-risk-verification` → `github:yeet` and contains no
executable publication implementation.

After final export and `personal-risk-verification: supported`, produce:

```yaml
publication_handoff:
  owner: github:yeet
  intent: publish_to_github
  repository:
  worktree:
  target_revision:
  exact_paths: []
  unrelated_state: []
  intended_remote:
  intended_base:
  confirmed_visibility:
  host_connection_entrypoint:
  completion_verdict: supported
  dependency_install_authorized: false
```

Publication intent does not authorize dependency installation. If an already
available ordinary Git path is sufficient for the requested stage, the
publication owner may use it. If a required helper is missing, it asks the user
instead of installing. The cached plugin source is external and is not modified
or promoted to a durable profile owner.

The audit/local-finish route and `github:yeet` publication route are
outcome-exclusive; choose one from the requested outcome and do not run both.
Do not install or enable a dependency for publication or `github:yeet` unless
that exact action is separately authorized.

The handoff is ready only when the candidate is unchanged since verification,
the exact paths are isolated, remote/base/visibility intent is known, and no
excluded or sensitive state is present. Otherwise stop after export and report
the missing evidence or decision.
