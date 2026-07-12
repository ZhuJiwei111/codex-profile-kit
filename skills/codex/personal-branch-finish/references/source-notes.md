# Source Notes

Checked: 2026-07-12.

This skill uses upstream branch-finishing material as design evidence, not as a
runtime dependency. Local authorization, user-change protection, worktree and
worker ownership, detached-job preservation, and specialist workflow boundaries
take precedence. Available Git history does not prove direct textual derivation
of the initial local skill.

## Superpowers `finishing-a-development-branch`

- Release: [v6.1.1](https://github.com/obra/superpowers/releases/tag/v6.1.1)
- Annotated tag object: `c984ea2e7aeffdcc865784fd6c5e3ab75da0209a`
- Peeled release commit: `d884ae04edebef577e82ff7c4e143debd0bbec99`
- Pinned skill:
  <https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/finishing-a-development-branch/SKILL.md>
- Upstream skill Git blob: `7f5337aaf9efff305db15836412106216dae4756`
- Upstream skill SHA-256:
  `e6d4a812de900d33c6eacfb40747f99427f25c304a7b7099120f9373b115a47f`
- Upstream file size: `6,832` bytes.
- License: MIT, Copyright (c) 2025 Jesse Vincent. See the
  [pinned license](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/LICENSE).
- License Git blob: `abf0390320aa14406af7a520b9b0739fdda9bf08`
- Audit note: GitHub release, annotated-tag, contents, and raw-file evidence
  agreed on the pinned object identities. One native `git ls-remote` attempt
  timed out; no clone was created.

## Technical References

The official Git documentation was used for command semantics, not copied as
workflow source material:

- [`git-worktree`](https://git-scm.com/docs/git-worktree): main and linked
  worktrees, porcelain fields, detached records, locks, removal, and prune.
- [`git-symbolic-ref`](https://git-scm.com/docs/git-symbolic-ref): attached and
  detached HEAD exit semantics.
- [`git-add`](https://git-scm.com/docs/git-add): pathspec, patch staging, and the
  whole-worktree scope of unqualified `git add -A`.

## Local History

- Initial local commit: `6574bce5f5ede8fb4566d0451ddcf613f7fdf8a5`
- Initial `SKILL.md` blob: `ae9009b29081290ee015a163c31b309735e2d449`
- Initial `agents/openai.yaml` blob:
  `9ce9447321eab2acadc7436cb98d85f074a53041`

## Adopted

- Detect the actual repository and worktree environment before offering a Git
  finish action.
- Treat detached HEAD differently from a named branch and preserve an external
  or harness-owned worktree.
- Keep a worktree after PR creation for later feedback.
- Require explicit destructive confirmation and avoid force-push without an
  exact request.
- Re-verify a merged or otherwise changed resulting state before claiming it is
  complete.

## Adapted

- Consume the local `personal-risk-verification: supported` verdict instead of
  rerunning a full test suite inside branch finish.
- Replace fixed option menus with per-action handoff, commit, and PR readiness.
- Separate Git main/linked state from task, coordinator, user, and harness
  ownership; path names are only clues.
- Split PR assessment, local preparation, branch push, and actual PR creation.
- Treat detached HEAD as safe for handoff but blocked for commit or PR until an
  authorized destination ref exists.
- Preserve approved detached jobs and invalidate earlier verification only when
  they change covered task state.

## Rejected

- Automatic `git pull`, local merge, push, branch deletion, worktree removal,
  or discard as part of a generic finish request.
- A fixed four-option or three-option menu with destructive cleanup offered by
  default.
- Inferring cleanup ownership from `.worktrees/` or `worktrees/` path names.
- Running `git worktree prune` after every removal.
- Guessing the base branch from `main` or `master` alone.
- Treating “push and create PR” as one implicit operation without verifying that
  both actions occurred.
- Copying POSIX shell assumptions, fixed remote names, or an unspecified
  workspace-exit tool into the local core workflow.

## Local Deviations

- Never use the goal of a clean worktree to justify staging, reverting,
  stashing, resetting, deleting, or reformatting unrelated user work.
- A generic finish request authorizes handoff only; every Git or external
  mutation remains bound to the requested outcome and exact target.
- Multiline workers default to handoff-only until coordinator intake, and the
  coordinator retains line decisions, cross-line conflict resolution, and
  integration provenance authority.
- Multiline finish handoffs preserve one provenance record per integrated line
  plus the final integration HEAD; they do not collapse several lines into one
  ambiguous checkpoint pair.
- Merge execution and destructive cleanup stay outside ordinary branch finish.
  Cross-line integration remains in `personal-multiline-coordination`.
- Job status, ETA, launch, monitoring, termination, and artifact cleanup retain
  their existing dedicated authorization boundaries.
