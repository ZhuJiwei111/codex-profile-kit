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
- `progress.md`: completed outcomes, most recent relevant checks, current
  blocker or running work, and a directly resumable next action.

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

Overwrite or fold in new information; do not append a transcript. Remove or
mark superseded detail when it no longer controls the task. Do not record every
tool call, raw output, complete timeline, repeated decision, inventory count, or
format-driven placeholder.

Update only when scope or a decision changes, a phase changes, evidence alters
the strategy, a blocker appears, or before compaction, handoff, stopping, or
closure. Keep task progress and durable findings distinct.

Before a final answer, handoff, compaction, stop, or closure following a
meaningful change, perform one consistency pass across all three files. Current
status and phase, running work, blocker, latest relevant check, and the one next
action must agree. In particular, completed or retired work must not remain
described as running, and superseded next actions must be folded away.

## Stop

At closure, mark the plan complete or superseded and fold the final outcome,
checks, remaining risk, and any real continuation point into the same files.
That terminal status ends implicit maintenance. Do not create automatic
archives, successor plans, hooks, validators, ledgers, Git actions, or a forced
continuation state machine.

This skill does not own grilling decisions, formal documentation, external-job
monitoring, or task-history reconstruction.

Read `references/source-notes.md` only when maintaining provenance.
