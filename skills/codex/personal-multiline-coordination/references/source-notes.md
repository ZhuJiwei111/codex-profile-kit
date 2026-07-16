# Source Notes

## Provenance

- Origin: local personal workflow derived from the user's Codex Desktop,
  worker, Git worktree, long-job, and recovery experience.
- External source text copied: none.
- External derivative license: not applicable.
- Repository license file: none present in `codex-profile-kit` at review time;
  this file therefore records provenance without asserting a redistribution
  license.
- Checked: 2026-07-12.

## Local History Reviewed

- `codex-profile-kit` commit `c5370e8` (2026-07-04), “Sync Codex profile
  writing and coordination skills”.
- `codex-profile-kit` commit `30a4f90` (2026-07-04), “Sync Codex profile kit
  2026-07-04”.
- `codex-profile-kit` commit `5ad41a7157352724ac51ad24f87949e3e23cc694`,
  the local manual integration provenance change: conflict-resolved integration
  uses `method: manual`, retains the source checkpoint through a named
  `preservation_ref`, does not claim mechanical source-patch equivalence, and
  includes the focused auditor regression test for that boundary.
- Pre-rewrite active skill, references, metadata, and registry-based auditor.

These commits are evidence of the local design lineage, not upstream APIs.

## Environment Evidence

- Codex version observed during design: `0.144.1` with multi-agent capability
  enabled in the current session.
- Git version observed: `2.34.1`; the auditor avoids depending on newer
  `git worktree ... -z` behavior.
- Auditor Git calls override repository fsmonitor, untracked-cache, and hook
  execution settings; a regression test confirms a configured fsmonitor is not
  invoked during inventory.
- Managed-subagent lifecycle tools were available in the current session.
- Live Desktop worker creation was explicitly excluded from this revision's
  smoke tests.
- The official Codex manual helper attempt returned HTTP 403 during the design
  review, so no undocumented Desktop task API or model-control behavior was
  assumed.

## Adopted

- Star coordination with coordinator-owned line decisions.
- Desktop-visible workers for top-level implementation lines and managed
  subagents for bounded auxiliary work.
- Event-driven supervision instead of periodic polling.
- Dependency, path/output conflict, and resource graphs for dynamic scheduling.
- One immutable worktree per writer and a dedicated integration worktree.
- Exact coordinator integration grants and source-to-integrated OID records.
- Repo-sibling fallback layout outside both the repository and `~/.codex`.
- Controlled symlink binding for ignored, immutable, project-local heavy data.
- App/Git/snapshot reconciliation with preservation-first recovery.
- Strict observer/executor separation: monitors report trigger evidence, the
  coordinator decides after intake, and the job-owning executor performs any
  separately authorized contingency.
- Manual-only routing for `personal-grilling`; normal questions, brainstorming,
  and one exact bounded executor status inspection remain the defaults.
- Optional existing schema-v2 snapshots for machine-checkable handoff;
  file-backed planning only after an explicit file-backed planning request.
- Exact-task continuation through a current-host metadata precheck and bounded
  task packet, without task enumeration or a restored context archive.

## Rejected Or Retired

- Permanent `.codex/multiline/registry.json` and `registry.md` sources of truth.
- Legacy lifecycle, recovery queue, archive entry, and `finish_candidate`
  state machine.
- Fixed concurrency targets and coordinator polling loops.
- Monitor-executed contingencies, including preauthorized ones.
- Implementation-worker commits, worker-owned integration grants, line `pass`,
  or next-stage launch. An assigned integration executor may perform only the
  exact internal checkpoint and integration mutations granted by the
  coordinator.
- Automatic `git add`, cleanup, force-removal, branch deletion, global prune,
  or permanent task deletion.
- Treating a symlink as mechanical write protection or sharing mutable project
  data across writers.
- Assuming a Desktop worker API, model, or reasoning-effort control that the
  active tool surface does not expose.
- Creating `.planning` files merely because coordination crosses sessions.

## Local Deviations And Limits

- The auditor reconciles Git plus an optional snapshot; it deliberately does
  not enumerate Desktop tasks, infer other-host state, or mutate anything.
- `immutable` is a coordination contract. The validator checks source location,
  Git ignore/tracking state, and symlink identity, not process-level write
  prevention.
- The revision includes unit and managed-subagent forward validation but no
  live App-visible worker smoke test.
- The active subagent and branch-finish contracts now use the same worker
  outcome, coordinator-decision, and integration-provenance boundaries.
