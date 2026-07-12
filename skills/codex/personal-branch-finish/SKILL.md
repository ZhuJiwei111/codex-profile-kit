---
name: personal-branch-finish
description: Use after a supported final-verification verdict for Git readiness, explicit commit or PR decisions, branch or worktree preservation, or repository handoff; not for verification, merge execution, or ordinary summaries.
---

# Personal Branch Finish

Consume a fresh `personal-risk-verification: supported` verdict and decide the
remaining repository handoff, commit, or PR readiness. Own Git and worktree
provenance, task-change isolation, and only the finish actions authorized by
the requested outcome.

A clean worktree is not the goal. Preserve unrelated changes, externally owned
workspaces, and approved detached jobs. Do not treat the words “finish” or
“complete” as authorization to stage, commit, push, create a PR, merge, delete,
or clean anything.

## Accept The Verification Handoff

Require a `supported` completion verdict and its state identity:

- the HEAD or source revision when applicable;
- the task-owned diff, artifacts, or paths it covered;
- checks not run and remaining risk; and
- the time or ordering of the last relevant mutation.

Use read-only Git inspection to confirm that state still applies. If a later
task-owned edit, generated-output change, commit hook, or detached job changed a
covered input or output, return to `personal-risk-verification`. Do not rerun or
reinterpret final verification here.

## Lock The Finish Request

Keep this record explicit when the checkout is linked or detached, the index is
already populated, workers are involved, ownership is mixed, or a detached job
depends on the worktree:

```yaml
finish_request:
  mode: handoff | assess_commit | commit | assess_pr | prepare_pr | create_pr | preserve
  authorized_actions: []
completion_input:
  verdict: supported
  verified_state_identity:
    head_oid:
    task_owned_diff_or_artifacts:
  not_run:
  remaining_risk:
coordination:
  actor_role: single_owner | coordinator | worker
  task_owner:
  coordination_id:
  coordinator_decision: pending | pass | no-go | needs-more-evidence | blocked
  coordinator_intake:
  integration_head_oid:
  line_records:
    - line_id:
      source_checkpoint_oid:
      integrated_oid:
git_intent:
  destination_branch:
  remote:
  pr_base:
detached_jobs:
  - job_id:
    owner:
    approval_scope:
    cwd:
    session_or_pid:
    launch_head:
    launch_inputs:
    log_path:
    output_path:
    status_command:
    success_failure_signals:
    worktree_dependency:
```

For a multiline handoff, populate only the coordination identifiers, decision,
intake, final integration HEAD, and one provenance record per integrated line
that current evidence provides. Omit those fields for a single-owner request
rather than inventing coordination state. A worker recommendation such as
`accept` is not a coordinator decision. Require `pass` before treating an
integrated multiline result as commit- or PR-ready; another coordinator state
may still be preserved in an accurate handoff without being promoted.

Map each multiline integration record's `source_oid` to
`source_checkpoint_oid` in this handoff. Keep its per-line `integrated_oid`
distinct from `integration_head_oid`, which identifies the final combined
integration state covered by final verification.

Keep it implicit for a simple known single-owner handoff. Read-only readiness
inspection needs no separate permission. A generic finish request without a
specific Git outcome authorizes handoff only.

## Inspect Provenance And Ownership

Read [Git readiness](references/git-readiness.md) before staging or committing,
preparing or creating a PR, handling a linked worktree or detached HEAD, or
reasoning about a populated index or cleanup request.

Determine from current-host evidence:

- canonical repository and worktree roots, Git common directory, HEAD OID, and
  attached, detached, or unborn branch state;
- main versus linked worktree, configured upstream, local ahead/behind snapshot,
  intended base, and any Git operation already in progress;
- task-owned, unrelated, and ambiguous staged, unstaged, and untracked changes;
- actor, task, line, worktree, and detached-job ownership; and
- whether the requested action would change files, refs, index, remote state,
  or resources that another owner still uses.

Do not infer ownership from a directory name, a clean-looking status, current
cwd alone, or the fact that a worker produced the files. A multiline worker is
handoff-only for Git mutations. After coordinator intake, only the coordinator
may create a source checkpoint or integrate under an explicit integration
grant. Later user-directed commit or PR work starts from the coordinator-owned
integration state, not from a worker line.

## Issue Per-Action Readiness

Keep readiness axes separate:

```yaml
finish_result:
  readiness:
    handoff: ready | blocked
    commit: ready | blocked | not_requested
    pr: ready | blocked | not_requested
  provenance:
    repo_root:
    git_common_dir:
    worktree_root:
    worktree_kind: main | linked
    branch_state: attached | detached | unborn
    branch:
    head_oid:
    upstream:
    ahead_behind:
    operation_in_progress:
  ownership:
    actor:
    task_owner:
    task_owned_changes:
    unrelated_changes:
    ambiguous_changes:
    preexisting_index:
  detached_jobs:
    preserved:
    blocked_actions:
  performed_actions:
  remaining_external_actions:
  blockers:
  required_authority:
  exact_next_action:
```

- Mark `handoff` ready when the current state, preserved changes, risks, and
  blockers can be reproduced accurately, even if a Git mutation is blocked.
- Mark `commit` ready only when verification is current, ownership is exact,
  the index can be preserved, and a named destination exists for detached HEAD.
- Mark `pr` ready only when commit reachability, source branch, remote, and base
  are unambiguous and the requested outcome authorizes the external action.
- Mark unrequested mutations `not_requested`; do not turn technical readiness
  into permission.

## Preserve Detached State Safely

Keep `detached_HEAD` and `detached_job` distinct:

- Detached HEAD does not block handoff. Record the exact OID. Without an
  authorized destination branch or ref, block commit and PR rather than
  attaching, switching, or creating a branch automatically.
- Preserve an approved `tmux`, `nohup`, scheduler, or other detached job. Do not
  stop, restart, close, monitor, or clean its artifacts from branch finish.
- Do not move, remove, switch, or mutate a worktree while a known job depends on
  its cwd, inputs, outputs, or launch provenance.
- If the job can still modify verified task state, return to final verification
  after that state stabilizes. If it is independent, preserve it and include
  its known handoff fields without broad process discovery.

For an unnamed ordinary status or ETA request, leave this specialist workflow
and use one bounded ordinary read-only status check. Use
`$personal-long-job-status` only after explicit skill invocation. Branch finish
does not acquire monitoring authority.

## Execute Only The Authorized Action

### Handoff Or Preserve

Make no Git or external mutation. Report the exact current state, ownership,
verification verdict, preserved changes and jobs, blockers, and one concrete
next decision when useful.

### Local Commit

An explicit commit request authorizes intentional staging of exact task-owned
paths or proven hunks and one factual local commit. It does not authorize push,
amend, merge, branch deletion, cleanup, or inclusion of unrelated changes.

- Never use `git add -A` or `git add .` for a mixed or user-owned worktree.
- Do not reset, unstage, stash, clean, or overwrite a preexisting index whose
  ownership is not exact.
- Inspect the cached file set and diff before committing.
- Generate a concise factual message when the user did not specify one and no
  repository convention requires a decision.
- After commit, inspect the actual commit and remaining worktree. If hooks or
  another actor changed task state, return to final verification.

### PR Assessment, Preparation, Or Creation

Treat “assess PR readiness” and “prepare PR” as read-only; drafting local PR
text is not creation. An explicit “create/open PR” request may authorize the
ordinary task-owned commit, branch push, and PR creation needed for that exact
outcome only when repository, source branch, remote, and base are unambiguous.
Record the actions before executing them and ask one decision-changing question
when a target is unresolved.

Do not force-push, merge, delete a branch or worktree, rerun remote CI, reply to
reviewers, resolve threads, or claim reviewer or CI acceptance. Preserve the
worktree for PR iteration.

## Exclude Merge And Cleanup Execution

Report merge, branch-deletion, discard, worktree-removal,
session-termination, and artifact-cleanup blockers or required ownership, but
do not execute those operations under ordinary branch finish. Cross-line
integration belongs to the coordinator; any destructive cleanup needs a
separate exact, recoverable authorization.

## Produce The Repository Handoff

Include only facts that help reproduce or continue the finish state:

- canonical repo/worktree path, branch state, HEAD OID, upstream/base snapshot;
- task-owned changes or resulting commit, and unrelated state left untouched;
- `supported` verification input, checks not run, and remaining risk;
- exact local and external actions actually performed;
- remaining actions and the authority or decision they require; and
- approved detached jobs or externally owned worktrees intentionally preserved.

Do not claim a commit, push, PR, CI result, review transition, merge, or cleanup
that did not occur.

## Collaboration And Boundaries

- `personal-risk-verification` owns the only final completion verdict and any
  re-verification after relevant state changes.
- `personal-multiline-coordination` owns line cards, coordinator intake,
  authoritative line decisions, cross-line conflicts, and integration
  provenance.
- `personal-subagent-boundaries` owns one-shot managed-subagent file ownership
  and reporting contracts. `personal-multiline-coordination` owns persistent
  Desktop worker line cards, worktrees, and coordinator intake. Neither worker
  type promotes its own recommended outcome.
- `personal-review-response` owns review disposition, remote CI interpretation,
  replies, and thread state.
- `$personal-long-job-status` owns one-shot job status and ETA only after
  explicit skill invocation. For an unnamed ordinary request, leave specialist
  workflows and use one bounded ordinary read-only status check. Long-running
  launch and monitoring authorization remain outside this skill.
- `personal-project-output-explainer` may decode an existing completion verdict
  or repository handoff only when the user explicitly expresses a comprehension
  need. It does not own ordinary status, summary, report, completion, or
  next-step output.

## Source Provenance

See [source notes](references/source-notes.md) for the pinned Superpowers source,
license, official Git references, local history, adopted ideas, rejected
automation, and Codex-specific deviations.
