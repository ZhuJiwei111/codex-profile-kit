# Cross-Skill Routing

Keep this skill as the multiline router. Do not copy the full rules from other skills; route to them at the right gate.

## Use With Other Personal Skills

- `personal-subagent-boundaries`: before creating worker, explorer, reviewer, validator, or monitoring subagents; use it for delegation contracts, exclusive file boundaries, and monitoring observer rules.
- Long-Running Jobs rules from durable instructions: before launching or supervising GPU jobs, downloads, evals, training, batch processing, or jobs expected to run longer than 10 minutes.
- `personal-branch-finish`: when a line reaches `finish_candidate` and the remaining work is commit, PR, merge, final summary, or clean handoff.
- `personal-risk-verification`: before claiming a line, branch, or coordination stage is complete.
- `personal-repo-intake`: when the repository itself is unfamiliar and basic edit surface, commands, or git state are unknown.
- `personal-context-compression` or `context-save-restore`: when handoff needs to survive a long session or context transition.

## Thread And Worktree Tools

If Codex app thread/worktree tools are available:

- Use them for read-only inspection when that resolves cwd, branch, ownership, or stale-thread ambiguity.
- Ask for explicit confirmation before creating, renaming, archiving, or handing off user-owned threads.
- Prefer app-native worktree mechanisms over manual `git worktree add` when available.

If only git is available:

- Detect whether the current checkout is already a linked worktree before creating another one.
- Follow project conventions for worktree location.
- Verify project-local worktree directories are ignored before using them.

## Worker Prompt Contract

Worker prompts should include:

- Line id and objective.
- Canonical cwd and branch.
- Exclusive editable paths.
- Read-only inputs.
- Allowed commands and long-job boundaries.
- Stop condition.
- Handoff path and required handoff fields.
- Maximum productive continuation budget.

Workers stop at `pass`, `no-go`, `needs-more-evidence`, or `blocked` and wait for coordinator intake.

## Do Not Route Automatically

Do not automatically start long monitoring, create workers, archive threads, commit, PR, merge, publish, clean artifacts, or mutate registry files only because an audit found risk. Report the risk and ask for or rely on explicit authorization for the action.
