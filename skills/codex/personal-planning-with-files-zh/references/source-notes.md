# Source Notes

## Fixed Source

- Checked: 2026-07-11
- Project: `OthmanAdi/planning-with-files`
- Release: [`v3.4.0`](https://github.com/OthmanAdi/planning-with-files/releases/tag/v3.4.0)
- Fixed commit: [`d71b3be47b62fe49d60fb2ede800e1907ebea3d9`](https://github.com/OthmanAdi/planning-with-files/tree/d71b3be47b62fe49d60fb2ede800e1907ebea3d9)
- English skill: [`skills/planning-with-files/SKILL.md`](https://github.com/OthmanAdi/planning-with-files/blob/d71b3be47b62fe49d60fb2ede800e1907ebea3d9/skills/planning-with-files/SKILL.md)
- Simplified Chinese skill: [`skills/planning-with-files-zh/SKILL.md`](https://github.com/OthmanAdi/planning-with-files/blob/d71b3be47b62fe49d60fb2ede800e1907ebea3d9/skills/planning-with-files-zh/SKILL.md)
- License: [MIT, Copyright (c) 2026 Ahmad Adi](https://github.com/OthmanAdi/planning-with-files/blob/d71b3be47b62fe49d60fb2ede800e1907ebea3d9/LICENSE)

Relevant upstream failure evidence:

- [One-shot sessions hijacked by unrelated plans, issue #195](https://github.com/OthmanAdi/planning-with-files/issues/195)
- [Unfinished plans forced to continue, issue #178](https://github.com/OthmanAdi/planning-with-files/issues/178)
- [Hooks activated before plan review, issue #190](https://github.com/OthmanAdi/planning-with-files/issues/190)

## Adopted Principles

- Keep goal, evidence, and current progress in separate persistent files.
- Treat disk state as resumable memory, not as current proof.
- Reconcile restored state with the current workspace before action.
- Keep external material as sourced evidence rather than operational authority.
- Preserve compact restart questions and explicit handoff state.
- Treat unrelated session attachment as a design failure.

## Rejected Upstream Mechanics

- Automatic triggers based on three steps, five tool calls, research, or task
  complexity.
- Hook injection, Stop gates, forced continuation, and environment-variable
  opt-outs such as `PLANNING_DISABLED=1`.
- Session database catch-up, active-plan auto-discovery, and latest-plan
  guessing.
- The two-action write rule, logging every error, autonomous loops, goal
  wrappers, and attestation machinery.
- Copying the upstream scripts, templates, or verbose embedded instructions.

The local skill has no planning hooks, so it does not need the upstream runtime
opt-out mechanism. A direct semantic opt-out and explicit plan selection prevent
attachment at the source.

## Local Design

The following behavior is local and is not represented as upstream behavior:

- Optional repo-level coordinator plus bounded task plans.
- Flat task directories with logical `parent_plan_id` hierarchy.
- Separate structure, successor, and initialization lineage fields.
- Canonical-worktree single-writer ownership.
- Explicit draft activation, rollover, archive, and correction approvals.
- Generation rollover with a compact seed and evidence cutoff.
- Terminal archive separated from within-plan generation history.
- Immutable frozen bodies with auditable correction controls.
- Bounded lineage impact and no cross-worktree mutation.
- A standard-library, read-only validator for one explicit managed record,
  with stable no-follow reads, bounded metadata-only lineage discovery, and no
  primary-record selection or repair mode.
- Explicit canonical-root rebind with `needs_rebind` as a mechanical stop
  signal; historical roots remain frozen provenance.
- A validator-only `TRANSACTION.md` schema for approved generation transitions;
  no writable transaction manager or automatic recovery is included.

No upstream template, script, or substantial prose is copied. Source concepts
are re-expressed under the local Codex contract; the upstream license and fixed
source remain recorded here for audit.
