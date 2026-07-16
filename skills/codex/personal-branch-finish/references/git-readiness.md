# Git Readiness Reference

Use this reference for local-only commit work, preservation, or a publication
handoff whenever linked worktrees, detached HEAD, an existing index, mixed
ownership, or cleanup pressure makes the state non-obvious. Keep all inspection
on the current host and target repository.

## Contents

- [Collect A Read-Only Snapshot](#collect-a-read-only-snapshot)
- [Interpret Repository State](#interpret-repository-state)
- [Resolve Base And Remote Intent](#resolve-base-and-remote-intent)
- [Separate Task And Index Ownership](#separate-task-and-index-ownership)
- [Assess And Execute A Local Commit](#assess-and-execute-a-local-commit)
- [Hand Off GitHub Publication](#hand-off-github-publication)
- [Preserve Worktrees And Jobs](#preserve-worktrees-and-jobs)
- [Detect Evidence Invalidation](#detect-evidence-invalidation)

## Collect A Read-Only Snapshot

Run only the commands needed for the requested readiness decision and inspect
each exit status. Typical commands are:

```bash
git rev-parse --show-toplevel
git rev-parse --absolute-git-dir
git rev-parse --git-common-dir
git status --porcelain=v2 --branch
git symbolic-ref --quiet --short HEAD
git rev-parse --verify HEAD
git worktree list --porcelain
git diff --name-status
git diff --cached --name-status
git ls-files --others --exclude-standard
```

Resolve relative Git paths against the canonical repository root before
comparing them. Treat `git symbolic-ref --quiet --short HEAD` exit status `1` as
detached HEAD, not a generic command failure. Treat an absent verifiable `HEAD`
as a possible unborn branch and inspect status before deciding.

Use `git rev-parse --git-path <marker>` and bounded file existence checks for
in-progress operations such as `MERGE_HEAD`, `CHERRY_PICK_HEAD`, `REVERT_HEAD`,
`rebase-merge`, `rebase-apply`, and `BISECT_LOG`. Do not start, continue, abort,
or repair an existing Git operation from readiness inspection.

Do not fetch, pull, contact a remote, print credential-bearing remote URLs, or
broadly scan processes merely to fill the snapshot. Record when upstream and
ahead/behind evidence comes only from existing local refs.

## Interpret Repository State

- `git-dir == git-common-dir` normally indicates the main worktree; different
  canonical paths indicate a linked worktree. Confirm the matching record in
  `git worktree list --porcelain`.
- The porcelain `branch` field identifies an attached branch; `detached`
  identifies detached HEAD. Record the full HEAD OID in either case.
- Git's main/linked classification does not prove worktree ownership. Establish
  `current_task`, `coordinator`, `user`, `harness`, or `unknown` ownership from
  creation records, a line card, native workspace state, or explicit user
  context.
- Directory names such as `.worktrees/` and `worktrees/` are clues only. Never
  use them as cleanup authority.
- A dirty worktree can still be ready for handoff or a scoped commit. Readiness
  depends on isolating task-owned state, not making status empty.
- Any merge, rebase, cherry-pick, revert, or bisect in progress blocks a new
  local commit or publication handoff unless the explicit task owns that
  operation and its next transition.

## Resolve Base And Remote Intent

Prefer finish intent in this order:

1. Explicit user request or approved plan.
2. Multiline Line Card, coordinator intake, or explicit publication target.
3. Configured upstream and locally recorded remote default branch.
4. A local merge-base comparison against a known candidate.

Do not guess a base merely because `main` or `master` exists. A merge base is a
commit, not proof of the intended destination branch. If destination branch or
publication target changes the requested action and remains ambiguous, ask one
targeted question.

When an upstream is configured, a bounded local snapshot may use:

```bash
git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}'
git rev-list --left-right --count '@{upstream}'...HEAD
```

Label the result as local-ref evidence unless a separately authorized fetch has
made it current. Do not make `git pull` an automatic finish step.

## Separate Task And Index Ownership

Partition staged, unstaged, and untracked state into:

- `task_owned`: created or modified by the authorized task, explicitly included
  by the user, or accepted by the multiline coordinator for this line;
- `unrelated`: known user, prior-stage, other-line, or generated state outside
  this finish action; and
- `ambiguous`: ownership or hunk boundaries cannot be established safely.

Do not equate current worktree contents with task ownership. Preserve intended
untracked task resources, but do not stage an untracked file merely because it
is present.

If the index already contains unrelated or ambiguous staged entries, do not
reset, unstage, overwrite, or silently include them. Mark commit blocked unless
an exact, user-approved isolation strategy preserves the existing index. If one
hunk mixes task and user changes and provenance is not exact, block rather than
guess.

## Assess And Execute A Local Commit

Require all of these before commit:

- current `personal-risk-verification: supported` evidence;
- exact task-owned paths or hunks and no unresolved ownership overlap;
- no conflicting Git operation in progress;
- attached branch, or an explicitly authorized destination ref for detached
  HEAD; and
- an explicit commit outcome covering the current task.

Stage only exact task-owned state:

```bash
git add -- <task-path>...
git add -p -- <task-path>...
git diff --cached --name-status
git diff --cached --check
git diff --cached
```

Use patch staging only when hunk ownership is already known; interactive choice
does not create provenance. Never replace these scoped commands with
`git add -A` or `git add .` in a mixed worktree.

Before commit, confirm the cached diff contains every intended task change and
no unrelated entry. After the authorized commit, inspect the actual commit OID,
file set, summary, and remaining status. A commit does not authorize push or
amend.

If a hook modifies task files, generated outputs, or the index beyond the
verified state, stop and return to final verification before another finish
claim or external action.

## Hand Off GitHub Publication

Branch finish does not assess, prepare, or execute a GitHub publication. When
the requested outcome includes push or a pull request, make no local commit for
that publication and hand the complete flow to `github:yeet`.

The handoff includes the `personal-risk-verification: supported` verdict,
repository and worktree, target revision, exact task-owned paths, unrelated
state left untouched, intended remote and base when known, and
`dependency_install_authorized: false`. Publication intent does not grant
dependency installation. Use an already available ordinary Git path when it is
sufficient; otherwise the publication owner asks rather than installing a
missing helper.

Detached HEAD, a branch already owned by another worktree, an ambiguous remote,
or an ambiguous base is reported as handoff evidence. Branch finish does not
create or switch a publication branch, push, contact GitHub, or mutate remote
state.

## Preserve Worktrees And Jobs

Preserve a main, linked, user-owned, harness-owned, coordinator-owned, or
unknown worktree unless a separate cleanup workflow proves ownership,
recoverability, no dependent job, and exact destructive authority. Ordinary
branch finish does not run `git worktree remove`, `git worktree prune`, branch
deletion, discard, reset, stash, or clean.

For each already-known approved detached job, preserve its owner, approval
scope, cwd, session or PID, launch HEAD and inputs, log/output paths, status
command, success/failure signals, and worktree dependency. Do not discover,
poll, terminate, restart, or clean the job from this workflow.

If the job still writes verified task inputs or outputs, block a local commit
or publication handoff until its state stabilizes and final verification runs
again. If it is independent, preserve it and report that it remains active
without claiming its status or ETA.

## Detect Evidence Invalidation

Return to `personal-risk-verification` when any finish action, hook, worker,
generator, or detached job changes a task-owned file, artifact, input, output,
or revision covered by the prior verdict. A local commit that records identical
verified content does not by itself invalidate behavior evidence, but inspect
the resulting commit and tree before relying on that conclusion.

Remote CI, pull-request creation, reviewer state, and merge results are separate
evidence domains. Never infer them from the local verdict or publication
handoff.
