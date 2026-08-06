---
name: personal-planning-with-files-zh
description: Use when the user explicitly asks to create or select a file-backed long-task plan, or when exactly one already-active repository plan clearly matches the current task and needs implicit continuation, reconciliation, handoff, or closure.
---

# Personal Planning With Files Zh

Use two compact current-state files as recoverable working memory. This does
not replace ordinary task planning, evidence, or project documentation.

## Activate One Plan

Creating the first plan or choosing among plausible plans requires an explicit
user request or invocation. Do not create or select a plan implicitly.

After a plan is created or selected, it is sticky for that task. The user does
not need to invoke this skill again. Invoke it implicitly on every substantive
continuation turn and after compaction when task context or a handoff identifies
the plan. Resume an existing plan implicitly only when exactly one active plan
clearly matches; ask when several remain plausible.

Use an isolated directory:

```text
<project-root>/.planning/plans/<YYYYMMDD>-<slug>/
```

Keep one primary writer; concurrent workers return evidence to that writer.

For a new plan, maintain only:

- `task_plan.md`: the sole owner of active, blocked, complete, or superseded
  status; current goal, scope and non-goals, success conditions, current phase,
  active blocker or running work, remaining phases, and one next action;
- `findings.md`: only facts, decisions, assumptions, unknowns, and evidence
  anchors or completed outcomes that still affect later work.

Do not create a new `progress.md`. When a selected existing plan already has
one, treat it as an optional legacy record: do not delete, reformat, or keep it
synchronized. Read it only when its still-relevant content is absent from the
two current owners, and fold that content into the appropriate owner during a
normal meaningful update.

An older plan without an explicit status may count as active only when its
unfinished current phase and next action clearly match the task.

## Continue The Active Plan

Read `task_plan.md` before making a state-dependent claim or action. Read
`findings.md` when the current action depends on earlier facts, after compaction
or handoff, or when the task plan lacks enough context. These files are memory,
not proof; compare a material disputed claim with the relevant live evidence
rather than revalidating the whole project.

Simple acknowledgements, isolated factual questions, and unrelated work do not
require a plan write. A meaningful state change does.

## Keep Current State

Overwrite or fold information into the file that owns it; do not append a
transcript. Retain completed outcomes in proportion to their continuing
importance when they still control future work. Preserve enough rationale and
evidence for scope changes, consequential decisions, critical gates, expensive
failures, and pitfalls that prevent costly repetition. Compact routine or
superseded detail when it no longer controls the task; never reduce an important
completed outcome mechanically because it is old. Do not record every tool
call, raw output, complete timeline, repeated decision, inventory count, or
format-driven placeholder.

Update only the owner whose state changed, such as after a scope or decision
change, phase transition, strategy-changing finding, blocker, compaction,
handoff, or closure. Before stopping after a meaningful change, make
`task_plan.md` directly resumable; update `findings.md` only if a continuing
fact or decision changed. Do not perform a format-driven cross-file consistency
pass.

## Coordinate With The Project Journal

When `personal-project-journal` is active, keep `task_plan.md` as the sole owner
of current task state and let JOURNAL own chronological event history. Update
the plan with what remains true and journal only a qualifying durable event;
link to canonical decisions and evidence rather than copying them. The journal
workflow is independently owned and is not a competing current-state ledger
created by this skill.

## Stop

At closure, mark `task_plan.md` complete or superseded and retain only outcomes,
evidence, or continuation facts that still matter in `findings.md`. That
terminal status ends implicit maintenance. Do not create automatic archives,
successor plans, hooks, validators, Git actions, or a forced continuation state
machine. Any qualifying project-journal entry is owned independently by
`personal-project-journal`.

This skill does not own grilling decisions, formal documentation, external-job
monitoring, or task-history reconstruction.

Read `references/source-notes.md` only when maintaining provenance.
