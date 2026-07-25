# Source Notes

Checked: 2026-07-25.

This local workflow comes from persistent Codex App tasks and Git worktrees.
Historical failures involved ambiguous task/cwd/worktree identity, overlapping
writers, inconsistent decisions across user-visible tasks, and several lines
publishing competing final states.

Managed subagents were separately reviewed and are short-lived, main-task
controlled workers rather than persistent user-facing lines. External-job
monitoring was also split into its own strict manual-only skill.

The retained preferences are exact identity, one writer per intersecting
surface, bounded independent deliverables, minimal cross-line state, one
integration owner, evidence-bearing handoff, and no task-count voting.
