---
name: personal-planning-with-files-zh
description: Manual only. Use only when the user explicitly invokes this skill to create or resume bounded repository-local working memory for a real long task across compaction, interruption, handoff, or fresh Codex tasks.
---

# Personal Planning With Files Zh

Use three compact current-state files as recoverable working memory. This does
not replace ordinary task planning, evidence, or project documentation.

## Select One Plan

Use an isolated directory:

```text
<project-root>/.planning/plans/<YYYYMMDD>-<slug>/
```

Create or resume exactly one user-selected or clearly matching plan. Ask when
several remain plausible. Keep one primary writer; concurrent workers return
evidence to that writer.

Maintain only:

- `task_plan.md`: current goal, scope and non-goals, success conditions, current
  phase, remaining phases, and one next action;
- `findings.md`: only facts, decisions, assumptions, unknowns, and evidence
  anchors that still affect later work;
- `progress.md`: completed outcomes, most recent relevant checks, current
  blocker or running work, and a directly resumable next action.

## Keep Current State

Overwrite or fold in new information; do not append a transcript. Remove or
mark superseded detail when it no longer controls the task. Do not record every
tool call, raw output, complete timeline, repeated decision, inventory count, or
format-driven placeholder.

Update only when scope or a decision changes, a phase changes, evidence alters
the strategy, a blocker appears, or before compaction, handoff, stopping, or
closure. Keep task progress and durable findings distinct.

## Resume And Stop

On resume, read all three files and reconcile them with current Git, code,
tests, and running-task evidence. The files are memory, not proof. Report stale
or conflicting state before proceeding.

At closure, fold the final outcome, checks, remaining risk, and any real
continuation point into the same files. Do not create automatic archives,
successor plans, hooks, validators, ledgers, Git actions, or a forced
continuation state machine.

This skill does not own grilling decisions, formal documentation, external-job
monitoring, or task-history reconstruction.

Read `references/source-notes.md` only when maintaining provenance.
