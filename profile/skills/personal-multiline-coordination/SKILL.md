---
name: personal-multiline-coordination
description: Coordinate persistent Codex App tasks, isolated Git worktrees, and cross-line intake; invoke implicitly only for read-only ownership reconciliation when existing task or worktree identity is ambiguous. Not for managed subagents or recurring external-job monitoring.
---

# Personal Multiline Coordination

Coordinate product-visible tasks that have their own persistent context and may
interact with the user. Do not treat them as managed subagents.

## Establish Identity And Ownership

For each active line, keep only the facts needed to prevent collision:

- task ID and user-visible purpose;
- actual `cwd`, repository, worktree, branch, and input revision;
- owner and exclusive write surface;
- dependencies, stop condition, and handoff evidence; and
- the single task that owns integration and final user-facing synthesis.

Resolve identity from current task/worktree evidence. Do not infer ownership
from titles or stale discussion. When identities are ambiguous, limit implicit
use to read-only reconciliation and ask before changing tasks or worktrees.

## Keep Lines Independent

Give each line a bounded deliverable that remains useful if another line stops.
Only one task writes an intersecting surface. Share decisions and evidence
through the smallest canonical project artifact or explicit message needed;
do not duplicate a whole parent discussion.

App tasks may ask the user questions and retain their own context. A decision in
one line is not automatically authority for another. The integration owner
checks source, revision, scope, and conflicts before accepting a handoff; do not
vote by task count or let several lines publish competing “final” states.

Use managed subagents for bounded one-shot internal workers. Use
`personal-monitor-external-jobs` for repeated observation of an external job.
Creating an App task still requires matching authority, and a monitoring
handoff is established only after the target acknowledges the exact job and
returns one successful initial status sample. A parent discussion task does not
duplicate routine polling.

## Intake And Stop

At handoff, require the result, changed paths or artifacts, fresh checks,
uncommitted state, omissions, blockers, and exact next owner. Stop a line when
its deliverable is complete, its decision belongs to the user or integration
owner, its write boundary overlaps, or further work needs new authority.

Do not create, archive, message, or mutate App tasks merely because this skill
was loaded; those actions require the matching user request.

Read `references/source-notes.md` only when maintaining provenance.
