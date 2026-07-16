---
name: personal-codex-audit
description: Use for current-host, whole-profile audit, drift comparison, export, apply, or preparation of a bounded sync across AGENTS.md, personal skills, hooks, and codex-profile-kit; GitHub publication is handed to github:yeet.
---

# Personal Codex Audit

## Contract

Own current-host, whole-profile inventory, drift analysis, and profile-kit
transfer decisions.

The main process locks direction, authority, host, repository, and transfer
scope, then owns intake. A bounded profile executor performs substantive audit,
export, fetch, integration, apply, and verification commands. Reviewers report
candidate-diff evidence and uncertainty only. The main process alone issues the
completion verdict or authorizes the next owner.

- Keep audits, comparisons, `sync.py audit`, and dry runs read-only.
- Require matching intent for writes and publication. Explicit directional sync
  intent authorizes the bounded ordinary chain defined below; a bare audit,
  comparison, export, or apply request does not authorize later stages.
- Distinguish files, configuration, enablement, trust, export state, and
  verification instead of collapsing them into "installed" or "active."
- Reconcile skill provenance, admission, activation, portability, and export
  as separate states. Whole-profile aggregation never grants admission to one
  candidate.
- Treat MCP declarations as configuration evidence only. Inventory their safe
  public identity without collecting authentication or runtime state.
- Preserve unrelated profile and repository changes.

## Scope Gate

| Requested outcome | Primary owner |
| --- | --- |
| Audit or compare the whole reusable profile | Deep audit path in `personal-codex-audit` |
| Routine directional sync to or from `codex-profile-kit` | Fast path in `personal-codex-audit` |
| Commit, push, and open a GitHub pull request for an outbound candidate | `github:yeet`, after `personal-risk-verification: supported` |
| Local-only commit without publication | `personal-branch-finish`, after `personal-risk-verification: supported` |
| Decide one skill, plugin, or hook lifecycle | `personal-skill-hygiene` |
| Admit one newly created or externally installed skill | `personal-skill-hygiene`, with the owning system author/installer for mechanics |
| Create or edit one skill | `skill-creator` |
| Create, migrate, or test one hook or Markdown guard | `personal-codex-hook-rules` |
| Discover/install a skill or create a plugin | The corresponding system skill |

Do not expand single-artifact work into a profile audit. For mixed requests,
finish the read-only profile finding, then hand each concrete change to its
owning workflow and authorization gate.

## Path Selection

- Use the deep audit path only for an audit request or when a sync escalation
  trigger is present.
- For a routine directional sync, read only
  [references/sync-policy.md](references/sync-policy.md). Do not run the
  whole-profile collector, compatibility reconciliation, or state-model report
  unless the fast path escalates.
- Before Git network access, read the current host connection contract when the
  active instructions route to one, and use its documented entrypoint. Do not
  improvise direct, proxy, API, or archive fallbacks first.

## Audit Workflow

1. Lock the current host and requested profile surfaces. Tasks, threads,
   sessions, and other-host state are not reusable-profile evidence.
2. Read [references/source-policy.md](references/source-policy.md). Memory
   content remains excluded unless the user requests a memory-informed audit.
3. Reconcile each personal source note and the reviewed third-party lock with
   the current skill inventory. Report `source_classification`,
   `provenance_status`, `admission_status`, and `portability_disposition`
   independently; route a single missing or conflicting decision to
   `personal-skill-hygiene`.
4. Run `scripts/collect_codex_profile.py --home "$HOME"`; treat its JSON as a
   bounded inventory, not proof of runtime behavior.
5. When Codex changed since the last verified baseline, read
   [references/compatibility-policy.md](references/compatibility-policy.md)
   and choose focused or broad revalidation from the affected contract, not
   version inequality alone.
6. For drift or transfer readiness, read
   [references/sync-policy.md](references/sync-policy.md), then run `sync.py
   audit` or an equivalent dry run before proposing a write.
7. Apply [references/profile-state-model.md](references/profile-state-model.md)
   and reconcile counts with the configuration sources actually in scope. Keep
   `unknown`, `not-collected`, `user-reported`, and `product-confirmed` distinct.
8. Report scope, inventory, drift, exclusions, unknowns, and recommendations
   requiring approval. Label any opted-in memory evidence as memory-derived.

## Routine Directional Sync

Treat these explicit outcomes as matching authority inside the configured
repository, branch, current host, and safe envelope. Do not ask again at each
internal stage that remains inside the exact requested chain:

- **Sync to GitHub** authorizes audit, export, final local verification, and a
  bounded publication handoff to `github:yeet`. That owner exclusively performs
  branch setup, staging, commit, push, and draft pull-request creation.
- **Sync GitHub updates to this host** authorizes fetch, non-conflicting
  integration, and confirmed apply of existing admitted portable targets with
  the standard timestamped backup.

Neither intent authorizes a ready-for-review transition, merge, visibility
change, another repository or host, conflict resolution with ambiguous
ownership, new admission, or excluded/sensitive state. Outbound sync authorizes
only the default draft pull request owned by `github:yeet`.

Run the smallest direction-specific chain:

1. Lock direction, repository, branch/upstream, visibility when publishing,
   current host, clean ownership, and the host network entrypoint.
2. For outbound sync, run `sync.py audit`, export once, inspect the exact diff,
   and obtain `personal-risk-verification: supported`. Then hand the unchanged
   candidate to `github:yeet` with repository, worktree, target revision, exact
   paths, remote/base/visibility intent, the host connection entrypoint, and
   `dependency_install_authorized: false`. The audit executor must not stage,
   commit, or push first.
3. For inbound sync, fetch, classify ancestry, integrate without conflict, run
   `sync.py audit` and one apply dry run, then apply the reviewed existing
   targets with backup and require a zero-drift post-apply audit.
4. Use one verification pass per unchanged state. Export already verifies its
   candidate and apply already verifies the repository; do not add a standalone
   `verify` beside either command unless a later mutation invalidated evidence.
5. Escalate according to `sync-policy.md`. Stop before a material mutation that
   falls outside the fast-path authority instead of degrading into a broad
   audit or repeated network experiments.
6. When resuming an interrupted chain, confirm the candidate identity and
   ownership, then reuse still-valid evidence and resume at the first incomplete
   stage. Do not reopen completed stages or a deep audit merely because work
   moved to another turn or task.

## Hard Boundaries

- Never read or output credentials, auth/session files, raw transcripts,
  SQLite state, caches, trust hashes, or approval history.
- Never serialize MCP commands, arguments, environment entries, bearer-token
  variable names or values, header names or values, OAuth state, or runtime
  health. An auth mechanism category is the maximum default projection.
- Never infer individual hook enablement or trust from files, registrations,
  feature flags, hashes, or prior reports; direct the user to `/hooks`.
- Never infer admission from file presence, successful installation,
  popularity, a curated label, source reputation, an allowlist, or export.
- A memory feature flag may be inventoried; memory content remains opt-in and
  outside ordinary export.
- Do not edit audited profile assets or manage another host without separate,
  concrete authority.
- Do not stage, commit, push, publish, change visibility, or contact external
  services without matching explicit authority. The two directional sync
  outcomes above are matching authority only for their bounded chains, and
  outbound publication still remains exclusively executed by `github:yeet`.

## Resources

- `scripts/collect_codex_profile.py` and `scripts/test_collect_codex_profile.py`: emit and test the safe schema-v3 inventory, including redacted MCP declarations.
- [references/source-policy.md](references/source-policy.md): allowed evidence, memory, symlink, host, and sensitive-source boundaries.
- [references/sync-policy.md](references/sync-policy.md): audit, export, apply,
  verification, and publication-handoff gates.
- [references/profile-state-model.md](references/profile-state-model.md): consistent evidence and state labels.
- [references/compatibility-policy.md](references/compatibility-policy.md): Codex baseline and contract-triggered revalidation.
- [references/source-notes.md](references/source-notes.md): official sources, checked versions, and local deviations.
