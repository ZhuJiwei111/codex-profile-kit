---
name: personal-subagent-boundaries
description: Use for bounded one-shot subagents that independently explore, edit an exclusive surface, review, or validate and then stop; not for persistent App tasks, worktrees, recurring monitoring, or final task verdicts.
---

# Personal Subagent Boundaries

Use a subagent only when a bounded independent line improves speed, isolation,
or review quality. Keep a simple critical-path action in the main process when
delegation would add more coordination than value.

This skill owns one-shot delegation and intake. Route persistent App tasks,
worktrees, and active monitoring to `personal-multiline-coordination`.

## Set A Bounded Contract

Give the worker enough context to act without inheriting the whole discussion.
The contract may be prose, bullets, or any compact structure, but it must make
these facts unambiguous:

- the goal and concrete deliverable;
- the inputs and their stable revision or artifact identity when freshness
  matters;
- the actual `cwd`;
- what may be read and the exclusive write boundary, including generated files
  and indirect command side effects;
- the stop condition, including when new authority or a decision is needed;
  and
- the evidence expected at handoff, including checks, changed paths, omissions,
  and uncertainty.

Pass only task-relevant context. Do not expose secrets or tell an independent
reviewer the desired conclusion.

Delegate only work that can stop at a useful boundary without another worker's
intermediate decision. Use one writer for an overlapping mutation surface and
bind concurrent readers to a stable input. If overlap, hidden dependencies, or
an unexpected side effect appears, stop and let the main process reassign or
serialize the work.

## Keep Roles Narrow

- The main process owns scope, authority, intake, synthesis, and the final task
  judgment.
- An executor performs only the assigned read, edit, command, or check and does
  not authorize a later stage.
- A reviewer may report source anchors, findings, uncertainty, and an
  evidence-supported recommendation. That recommendation is non-authoritative;
  the main process evaluates it and decides.

Do not decide by worker count or votes. Do not let a worker stage, commit, push,
publish, contact external parties, launch a next stage, or mutate another
surface unless that exact action is authorized and included in its contract.

When the user selected a particular executor or independent review, do not
silently replace it with the main process or another executor kind. Wait for a
slot or request an explicit fallback. Optional delegation may remain local if
the original outcome and independence needs are preserved.

## Stop, Report, And Intake

At the stop condition, return a concise report in any useful format. Include
the result, changed paths, evidence with command outcomes or artifact identity,
and material omissions or risks. Ask for a new decision instead of expanding
scope, authority, resources, or ownership.

The main process confirms that the report came from the assigned worker and
input, inspects relevant changes or artifacts, checks the mutation boundary,
and decides whether the evidence is fresh enough to use. A worker report is
evidence, not task completion.

Use `personal-risk-verification` after all task-owned changes for the final
completion judgment. Use `personal-branch-finish` only for a separately
requested Git outcome.

See [source notes](references/source-notes.md) only when maintaining this
skill's provenance.
