---
name: personal-codex-audit
description: Use for current-host, whole-profile audit, drift comparison, export, apply, or sync across AGENTS.md, personal skills, hooks, and codex-profile-kit; not single-artifact work.
---

# Personal Codex Audit

## Contract

Own current-host, whole-profile inventory, drift analysis, and profile-kit
transfer decisions.

- Keep audits, comparisons, `sync.py audit`, and dry runs read-only.
- Require matching intent for export, confirmed apply, commit, push, or
  publication; one stage does not authorize the next.
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
| Audit or compare the whole reusable profile | `personal-codex-audit` |
| Export, apply, or sync `codex-profile-kit` | `personal-codex-audit` |
| Decide one skill, plugin, or hook lifecycle | `personal-skill-hygiene` |
| Admit one newly created or externally installed skill | `personal-skill-hygiene`, with the owning system author/installer for mechanics |
| Create or edit one skill | `skill-creator` |
| Create, migrate, or test one hook or Markdown guard | `personal-codex-hook-rules` |
| Discover/install a skill or create a plugin | The corresponding system skill |

Do not expand single-artifact work into a profile audit. For mixed requests,
finish the read-only profile finding, then hand each concrete change to its
owning workflow and authorization gate.

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

## Sync Workflow

1. Establish direction and the furthest authorized stage. Inspect profile-kit
   status and stop if a write could absorb unrelated changes.
2. Run `python3 scripts/sync.py audit` before export, apply, or publication.
3. Before export, require every portable personal skill to have a source note
   and every allowlisted vendor to match the reviewed third-party lock. A
   host-only, unassessed, deferred, rejected, or unlocked candidate is not an
   export source.
4. After explicit export authority, run `export`, `verify`, and
   `git status --short`; do not infer commit or push authority.
5. Run `apply` without `--confirm` first. Confirm only after approval of its
   target set and backup behavior.
6. Treat commit and push as separate external actions. Do not run
   `sync.py push --confirm` until both are authorized and the intended diff is
   isolated.

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
  services without matching explicit authority.

## Resources

- `scripts/collect_codex_profile.py` and `scripts/test_collect_codex_profile.py`: emit and test the safe schema-v3 inventory, including redacted MCP declarations.
- [references/source-policy.md](references/source-policy.md): allowed evidence, memory, symlink, host, and sensitive-source boundaries.
- [references/sync-policy.md](references/sync-policy.md): audit, export, apply, commit, and push gates.
- [references/profile-state-model.md](references/profile-state-model.md): consistent evidence and state labels.
- [references/compatibility-policy.md](references/compatibility-policy.md): Codex baseline and contract-triggered revalidation.
- [references/source-notes.md](references/source-notes.md): official sources, checked versions, and local deviations.
