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
- Preserve a worktree after an external publication owner creates a pull
  request so later feedback remains reproducible.
- Require explicit destructive confirmation and avoid force-push without an
  exact request.
- Re-verify a merged or otherwise changed resulting state before claiming it is
  complete.

## Adapted

- Consume the local `personal-risk-verification: supported` verdict instead of
  rerunning a full test suite inside branch finish.
- Replace fixed option menus with per-action local handoff, local-only commit,
  preservation, and publication-owner handoff readiness.
- Separate Git main/linked state from task, coordinator, user, and harness
  ownership; path names are only clues.
- Delegate the full GitHub commit, push, and pull-request flow to `github:yeet`
  so branch finish cannot create a duplicate preparatory commit.
- Treat detached HEAD as safe for handoff but blocked for a local-only commit
  until an authorized destination ref exists.
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
- Ordinary job status is one bounded executor observation; launch, active
  monitoring, termination, and artifact cleanup retain separate authorization
  boundaries.
- Publication handoffs explicitly set `dependency_install_authorized: false`.
  The cached `github:yeet` source remains external and is not a durable profile
  owner; missing helpers require an already available path or a user decision.

```yaml
skill_admission:
  skill: personal-branch-finish
  acquisition_mode: created
  source_classification: hybrid
  provenance_status: partial
  admission_status: legacy-exception
  portability_disposition: internalized
  safety_status: passed
  safety_review: "static_pass: Static review found no bundled executable; Git, cleanup, and publication mutations remain behind explicit authority and specialist ownership."
  trigger_status: passed
  trigger_review: "static_pass: The post-verification Git-readiness trigger was reviewed against personal-risk-verification, multiline integration, and github:yeet publication ownership."
  validation_status: passed
  validation:
    - "static_pass: Pinned upstream identities, license, local blobs, and declared derivation gap reviewed on 2026-07-16."
    - "static_pass: Targeted personal-skill admission validator fixtures passed on 2026-07-16."
  update_owner: "maintainer of personal-branch-finish"
  update_rule: "No update is authorized; any content, source, trigger, executable, or metadata change requires a fresh re-admission before portable export."
  rollback_basis: "The pre-batch rollback source is exact codex-profile-kit revision 3791645f59c0eeec497755bd7301be78b44efbea and exact tree ff0d3a66a8fd6962fa2050cd02a982a7fd03cff2; the current compatibility-only allowed content is separately locked by the validator's reviewed sha256-path-content-v1 full-tree digest."
  unknowns_disposition: provenance-gap
  unknowns:
    - "Available Git history does not prove whether the initial local text was directly derived from the pinned upstream skill."
```
