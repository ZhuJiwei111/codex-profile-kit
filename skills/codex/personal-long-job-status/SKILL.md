---
name: personal-long-job-status
description: Use only when explicitly invoked for one bounded, read-only status and ETA check of a known local long-running job or an observable current or parent Codex task. Do not launch or monitor jobs, diagnose or repair failures, run verification, control tasks, scan for unknown jobs, or estimate hidden model work.
---

# Personal Long Job Status

Produce one bounded status snapshot, then stop. Observe a target that the user or
visible conversation context already identifies; do not take ownership of the
job, task, or its next stage.

## Lock The Target And Boundary

Accept exactly one of these targets:

- a known local job identified by an exact PID plus launch identity, `tmux`
  session, scheduler job ID, command handoff, log path, output path, or expected
  artifact;
- the observable current or parent Codex task when its state is available in
  the conversation or product surface.

If neither target is identifiable, report `unknown` and request only the
smallest useful clue: task name, exact PID/session/job ID, or known log, output,
or artifact path. Do not discover a target by scanning processes, repositories,
the home directory, Codex session databases, or unrelated logs.

Stay read-only. Do not launch, poll, watch, tail continuously, stop, repair,
restart, re-run, parallelize, verify, approve, or advance work. A request that
also asks for one of those actions receives the snapshot first and then routes
the additional action to its owner and authorization boundary.

## Preserve Model And Task Ownership

- Do not require, switch, or claim to switch the current or parent task's model
  or reasoning effort. Do not treat the parent's setting as a baseline.
- If the caller separately selects a status-agent surface whose model and
  reasoning controls are actually available, choose the least costly setting
  sufficient for the evidence: routine/low for direct facts or balanced/medium
  for sparse ETA inference. Report a setting only when it is verifiable.
- Do not create a status or monitoring agent from this skill. Active-monitor
  profile selection belongs to `personal-subagent-boundaries` after explicit
  current-stage authorization.
- Treat native Goal or task controls, including pause, resume, edit, clear, and
  authoritative product state, as user/product-owned. Observe them when
  visible; never simulate a control transition.

## Run One Status Pass

1. Record the observation time and the target identifiers already in scope.
2. For a local job, read [evidence and ETA](references/evidence-and-eta.md) and
   use only the smallest safe probe that can change the answer. Prefer exact
   identifiers and known artifacts over command text or raw logs.
3. Classify these dimensions separately:
   - **Process state:** `running`, `exited`, or `unknown`.
   - **Progress state:** `advancing`, `suspected-stall`, `complete`, `failed`,
     or `unknown`.
   - **Completion evidence:** `confirmed`, `not-confirmed`, or `unknown`, with
     the exact success, failure, exit, or artifact signal.
4. Estimate remaining time only from measurable work units or an observable,
   bounded remaining step. Otherwise report ETA as `unknown` and state the
   missing evidence.
5. Return the snapshot and exit. Suggest at most one reproducible next status
   check; do not schedule or perform it.

Process disappearance is not success, a stale log is not failure, a reached
unit count is not necessarily a valid final artifact, and a reused PID is not
the original job. This skill never issues the task-level completion verdict.

For an observable Codex task, summarize only its visible phase, completed and
remaining work, blocker, and next bounded step. Give an ETA only when external
commands, artifacts, or explicit remaining work make it supportable. Never
estimate hidden model reasoning, private deliberation, or time-to-answer. If a
side conversation cannot observe its parent, return `unknown`; do not inspect
session JSONL, SQLite state, or other private task storage to reconstruct it.

## Report The Snapshot

Use this compact shape and omit fields that are genuinely inapplicable:

```yaml
target:
observed_at:
process_state:
progress_state:
completion_evidence:
evidence:
eta:
confidence:
next_safe_check:
```

Keep evidence to one or two decisive facts, with secrets redacted. Distinguish
an observation from an inference and explain `unknown` without manufacturing a
range. For a Codex task, use `process_state: not-applicable` when no external
process is the target.

## Route Adjacent Work

- Global `AGENTS.md` owns long-job launch approval, resource scope, startup
  guard, and reproducible handoff.
- `personal-subagent-boundaries` owns an explicitly authorized active-monitor
  worker; `personal-multiline-coordination` owns persistent visible worker
  lines, worktrees, and coordinator intake.
- `personal-evidence-debugging` owns investigation or repair after an observed
  failure, hang, or anomaly when the user authorizes that work.
- `personal-risk-verification` owns the only final task-completion verdict and
  any required final checks.
- Native Scheduled tasks or automation own recurring background status checks.
  This skill does not emulate a scheduler.

See [source notes](references/source-notes.md) for local history, official Codex
evidence, adopted constraints, and deliberate deviations.
