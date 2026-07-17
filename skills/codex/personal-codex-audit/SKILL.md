---
name: personal-codex-audit
description: Use for a read-only audit of the current host's reusable Codex profile, an outbound sync from the host to codex-profile-kit, or an inbound sync from a reviewed codex-profile-kit revision to the host. Manages portable AGENTS.md rules, personal-* Codex skills, and other explicit sync.py targets while excluding non-personal skills, HOST_LOCAL.md/config.toml, credentials, and runtime state; hand GitHub publication to github:yeet.
---

# Personal Codex Audit

## Select One Intent

| Intent | Outcome | Write boundary |
| --- | --- | --- |
| `audit` | Report managed assets, exclusions, and host/repository drift | Read-only |
| `sync up` / `outbound` | Export a reviewed candidate from this host into `codex-profile-kit` | Repository files only; publication is a separate handoff |
| `sync down` / `inbound` | Integrate a reviewed repository revision and apply its managed targets to this host | Active profile only after an exact dry run and timestamped backup |

Do not infer one intent from another. A bare audit, comparison, export, or dry
run does not authorize apply or publication. Treat an explicit directional
sync request as authority for its ordinary local chain, but stop when a
conflict, credential step, new admission decision, or other scope expansion
needs the user.

Run the commands on the user's behalf. Ask the user for an action only when
their permission, authentication, repository-visibility decision, or conflict
resolution is actually required.

## Keep The Portable Boundary Exact

- Use the current host and the explicitly selected `codex-profile-kit`
  worktree. Preserve unrelated profile, worktree, and index state.
- Migrate only Codex skill directories named `personal-*`. Treat every such
  skill already present in the canonical repository as a migration asset.
  Routine audit, export, and apply do not re-run source-note, admission, or
  provenance parsing.
- Before a newly created or externally acquired skill first enters the
  canonical repository, route its admission to `personal-skill-hygiene`. Once
  admitted there, repository membership is the routine sync boundary.
- Leave active non-personal skills unmanaged. Do not copy, update, classify as
  drift, retire, or delete them, whether they live under `~/.codex/skills` or
  another discovery root.
- Treat `rules/AGENTS.portable.md` as the complete portable rules file. During
  confirmed apply, back up the existing `~/.codex/AGENTS.md`, then replace it
  with that file; do not merge fragments into the old rules.
- Never apply `~/.codex/HOST_LOCAL.md`, `~/.codex/config.toml`, credentials,
  auth/session files, connection state, caches, memories, logs, or other
  runtime state. Templates for those surfaces are references only.

Read [source policy](references/source-policy.md) before inspecting the active
profile. Read [sync policy](references/sync-policy.md) for either directional
sync.

## Audit Read-Only

1. Lock the current host, repository, managed surfaces, and requested depth.
2. Run `scripts/sync.py audit` and inspect its categorized drift. Use
   `scripts/collect_codex_profile.py` only when the user needs a bounded safe
   inventory beyond transfer drift.
3. Report managed differences, excluded surfaces, unknowns, and any later
   action requiring separate authority. Do not export, apply, fetch, stage, or
   publish.

## Sync Outbound

1. Confirm repository and index ownership, branch/upstream, and the intended
   remote before any write or network action.
2. Run audit, export once, and inspect the exact resulting diff. Require secret,
   path, and symlink containment and preserve repository-only personal skills.
3. Obtain a fresh `personal-risk-verification: supported` verdict for the
   unchanged candidate.
4. Treat `sync up` or `sync to GitHub` as an explicit publication outcome and
   hand the candidate to `github:yeet`. Treat a bare `export` as local only.
   Do not stage, commit, push, or open a pull request in this skill.

## Sync Inbound

1. Fetch through the current host's documented network path, classify Git
   ancestry, and integrate only without conflicts or ambiguous ownership.
2. Run audit, then one exact `apply` dry run. Confirm that every planned target
   is managed and that excluded, non-personal, and host-only personal skill
   state is untouched.
3. Treat the dry run as the exact list for the inputs it observed, not a
   cross-command binding. Immediately before confirm, re-identify the
   repository revision, profile candidate, and target list. If all three are
   unchanged, run `apply --confirm` immediately; otherwise return to the dry
   run. When changes exist, record the timestamped backup path; an empty plan
   is a no-op and creates no backup. Then run a post-apply audit and require
   zero repository-to-host drift for managed targets.
4. If apply fails, stop and report whether its transactional rollback restored
   the previous state. If a later post-audit fails after successful apply,
   preserve the emitted backup and report the exact rollback source and
   affected paths. Do not improvise a broader overwrite.

## Stop Conditions

Stop before mutation when ownership is unclear, ancestry is ambiguous, a Git
conflict appears, the dry run changes after review, a path escapes its allowed
root, a source or destination is an unsafe symlink, a secret-bearing surface
appears, or the operation would touch an unmanaged asset. Keep routine checks
to these safety and transfer gates; do not add unrelated lifecycle,
compatibility, or repeated verification ceremony.

Use one verification pass for each unchanged state. Rerun only the evidence
invalidated by a later mutation. Never treat local export or verification as
implicit publication authority.

## Resources

- `scripts/collect_codex_profile.py`: optional safe current-host inventory for
  an audit that needs more than transfer drift.
- `scripts/test_collect_codex_profile.py`: focused collector tests.
- [source policy](references/source-policy.md): safe sources and exclusions.
- [sync policy](references/sync-policy.md): exact outbound/inbound execution
  and recovery gates.
