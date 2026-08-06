---
name: personal-planning-with-files-zh
description: Use when the user explicitly asks to create or select a file-backed long-task plan, or when exactly one already-active repository plan clearly matches the current task and needs implicit continuation, reconciliation, handoff, or closure.
---

# Personal Planning With Files Zh

Use three compact current-state files as recoverable working memory. This does
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

Maintain only:

- `task_plan.md`: active, blocked, complete, or superseded status; current goal,
  scope and non-goals, success conditions, current phase, remaining phases, and
  one next action;
- `findings.md`: only facts, decisions, assumptions, unknowns, and evidence
  anchors that still affect later work;
- `progress.md`: completed outcomes retained in proportion to their continuing
  importance, most recent relevant checks, current blocker or running work, and
  a directly resumable next action.

An older plan without an explicit status may count as active only when its
unfinished current phase and next action clearly match the task.

## Continue Every Substantive Turn

At the start of a substantive continuation, read all three files before making
a state-dependent claim or action. Reconcile them with current Git, code,
tests, task handoffs, and running-job evidence. The files are memory, not proof.
Report and repair stale or conflicting state before proceeding.

Simple acknowledgements, isolated factual questions, and unrelated work do not
require a plan write. A meaningful state change does.

## Keep Current State

Overwrite or fold in new information; do not append a transcript. Retain
completed outcomes in proportion to their future and audit importance. Preserve
enough rationale and evidence for scope changes, consequential decisions,
critical gates, expensive failures, and pitfalls that prevent costly
repetition. Compact routine or superseded detail when it no longer controls the
task; never reduce a completed phase mechanically to one line merely because it
is old. Do not record every tool call, raw output, complete timeline, repeated
decision, inventory count, or format-driven placeholder.

Update only when scope or a decision changes, a phase changes, evidence alters
the strategy, a blocker appears, or before compaction, handoff, stopping, or
closure. Keep task progress and durable findings distinct.

Before a final answer, handoff, compaction, stop, or closure following a
meaningful change, perform one consistency pass across all three files. Current
status and phase, running work, blocker, latest relevant check, and the one next
action must agree. In particular, completed or retired work must not remain
described as running, and superseded next actions must be folded away.

## Coordinate With The Project Journal

When `personal-project-journal` is active, keep this plan as the sole owner of
current task state and let JOURNAL own chronological audit history. Update the
plan with what remains true and journal only the substantive delta; link to
canonical decisions and evidence rather than copying them into both records.
The journal workflow is independently owned and is not a competing current-state
ledger created by this skill.

## Stop

At closure, mark the plan complete or superseded and fold the final outcome,
checks, remaining risk, and any real continuation point into the same files.
That terminal status ends implicit maintenance. Do not create automatic
archives, successor plans, hooks, validators, Git actions, or a forced
continuation state machine. Any active project-journal entry is owned
independently by `personal-project-journal`.

This skill does not own grilling decisions, formal documentation, external-job
monitoring, or task-history reconstruction.

Read `references/source-notes.md` only when maintaining provenance.
