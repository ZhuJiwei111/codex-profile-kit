---
name: personal-branch-finish
description: "Manual only. Use after final local verification when the user explicitly requests one Git outcome: repository handoff, local commit, commit plus non-force push, or non-force push only; use github:yeet only for an end-to-end branch, commit, push, and draft-PR outcome."
---

# Personal Branch Finish

Run only for an explicit Git result. Do not infer Git authority from “finish,”
“complete,” a clean worktree, or a positive verification conclusion.

Supported outcomes are:

- `handoff`: inspect and report without Git mutation;
- `commit`: stage exact task-owned changes and create one local commit;
- `commit + push`: create that commit and push its exact ref without force; or
- `push only`: push an already existing exact local commit/ref without creating
  or changing a commit.

If the requested result is the complete branch setup, commit, push, and draft
pull-request flow, hand the whole outcome to `github:yeet`. Do not make a
preparatory commit or push first. Branch finish does not create pull requests.

## Confirm The Exact Outcome And State

Before a Git mutation, require a fresh positive
`personal-risk-verification` conclusion whose evidence still covers the exact
task-owned state and commit/tree to be published. A read-only handoff may
instead report that verification is missing or stale.

Inspect the canonical repository and worktree, attached branch or detached
state, HEAD, configured upstream, current operation markers, staged/unstaged/
untracked changes, and exact task-owned paths or hunks. Separate unrelated and
ambiguous state. Resolve the exact remote, source ref or commit, and destination
ref for any push.

Stop before mutation when ownership is ambiguous, a merge/rebase/cherry-pick or
other Git operation is active, an existing index entry cannot be preserved, a
worker or job can still alter verified state, or the requested remote/ref is
not exact. Do not reset, unstage, stash, clean, switch, pull, merge, rebase,
amend, delete, or repair state to make the outcome easier.

## Handoff

Make no Git or external change. Report the repository/worktree, branch and HEAD,
task-owned and unrelated state, verification evidence identity, blockers, and
the exact next Git decision or authority if one remains.

## Commit

For an explicit local commit:

1. Preserve every unrelated staged, unstaged, and untracked change. Stage only
   exact task-owned paths with `git add -- <path>...` or proven task-owned hunks
   with `git add -p -- <path>...`. Never use `git add .` or `git add -A` to
   infer scope.
2. Inspect the complete cached file set and diff, and run
   `git diff --cached --check`. Require all intended changes and no unrelated
   entry.
3. Create one factual commit using the user's message or a concise repository-
   appropriate message. This does not authorize amend, a second commit, push,
   merge, cleanup, or publication.
4. Inspect the resulting commit OID and tree, changed file set, post-commit
   index, and worktree. If a hook changed covered content or generated output,
   stop and return to final verification before any further Git action.

Do not automatically attach a detached HEAD or create/switch a branch. A named
destination requires the user's exact requested outcome.

## Non-Force Push

For `commit + push`, complete the commit path first and then push that resulting
commit. For `push only`, do not stage or commit anything; confirm that the
selected existing commit and tree are exactly the verified state.

Push directly and without force to the exact destination, conceptually:

```text
git push <remote> <exact-source-ref-or-commit>:<exact-destination-ref>
```

Do not use `--force`, `--force-with-lease`, an implicit wildcard, or an
unresolved default ref. A non-fast-forward rejection, remote change,
authentication problem, hook mutation, or ambiguous source/destination stops
the outcome; do not retry with broader authority. Confirm the remote result
from the push response and report the actual local commit plus remote ref.

Push authority does not authorize dependency installation, branch creation,
pull-request creation, CI reruns, review-state changes, merge, branch deletion,
worktree removal, or cleanup.

## Report The Actual Result

State which of the four outcomes was requested, the exact repository/worktree,
branch, commit and remote ref involved, task-owned and unrelated state, actions
actually performed, verification evidence consumed, and any remaining risk or
external action. Never imply that a commit, push, PR, CI result, or cleanup
occurred when it did not.

See [source notes](references/source-notes.md) only when maintaining this
skill's provenance.
