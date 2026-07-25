---
name: personal-subagent-boundaries
description: Use for bounded one-shot subagents that independently explore, edit an exclusive surface, review, or validate and then stop; not for persistent App tasks, worktrees, recurring monitoring, or final task verdicts.
---

# Personal Subagent Boundaries

Delegate only when an independent bounded line materially improves speed,
isolation, or review quality.

Give the worker the smallest useful context: goal, concrete deliverable, actual
`cwd`, stable input or revision, read boundary, exclusive write boundary, stop
condition, and expected evidence. Use the minimum useful `fork_turns` or a
curated packet. Do not leak the desired conclusion to an independent reviewer.

Use one writer for intersecting mutation surfaces. A worker must stop rather
than ask the user, expand authority, touch another surface, perform Git or
external actions, or start a later phase. Persistent App tasks, worktrees, and
monitoring belong to their separate workflows.

The main task owns scope, decisions, user interaction, intake, synthesis, and
the final verdict. Evaluate worker evidence; do not vote by worker count or
repeat the entire assignment after a sufficient handoff.

At the stop condition, require the result, changed paths, checks or source
anchors, omissions, and uncertainty. Unexpected overlap or missing authority
returns to the main task.

Read `references/source-notes.md` only when maintaining provenance.
