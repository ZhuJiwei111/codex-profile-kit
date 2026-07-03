---
name: personal-multiline-coordination
description: Coordinate multiple Codex worker threads, git worktrees, long-running job lines, staged handoffs, registry audits, recovery queues, decision records, and finish gates. Use when the user explicitly asks for multiline/worktree coordination, or when multiple worktrees/workers create ownership, cwd, branch, handoff, monitoring, or merge-risk ambiguity; if triggered implicitly, start with read-only audit and do not write registry files or operate workers until the user confirms.
---

# Personal Multiline Coordination

## Overview

Use this skill as a lightweight, Trellis-inspired router for multi-line Codex work. It manages lines, gates, recovery, and handoff discipline without making Trellis CLI or `.trellis/` a default dependency.

## Core Rule

Start with truth from the workspace. Run or emulate the read-only audit before asking the user for facts that can be discovered locally.

If this skill was triggered implicitly because multiple worktrees, workers, or branches look risky, only audit and explain the risk. Do not create worktrees, write `.codex/multiline/*`, edit planning files, archive workers, start jobs, commit, merge, or open PRs until the user explicitly confirms that action.

## Workflow

1. Identify whether you are acting as `coordinator`, `worker`, or `monitoring observer`.
2. Run a read-only audit:
   `python3 "$HOME/.codex/skills/personal-multiline-coordination/scripts/audit_multiline.py" <project-root>`
3. Read `references/registry.md` before creating, checking, or updating `.codex/multiline/registry.json` or `registry.md`.
4. Read `references/lifecycle.md` before opening, continuing, stopping, restarting, archiving, or finishing a line.
5. Read `references/routing.md` before involving worker threads, subagents, long-running jobs, verification, commits, PRs, or merge/finish decisions.
6. Read `references/recovery.md` before recording checkpoints, decision records, recovery queue items, archive entries, or revive candidates.
7. Produce one of these outputs:
   - `Audit Summary`: current worktrees, registry state, mismatches, risks, and recommended next safe action.
   - `Line Card`: objective, canonical cwd/branch, owner/thread, scope, exclusive files, stop condition, handoff path, and verification expectation.
   - `Coordinator Intake`: evidence from worker handoff, git state, artifacts, decision, risks, and next gate.
   - `Locked Coordination Brief`: goal, active lines, non-goals, acceptance criteria, key decisions, risks, and remaining open questions.

## Authority Boundaries

- The coordinator owns global scope, registry writes, line creation, intake, finish gates, and archive decisions.
- A worker owns one actual Codex thread cwd, one canonical worktree/branch, one bounded line card, and line-local handoff files.
- A monitoring observer is read-only and follows the long-running job rules from the user's durable instructions and `personal-subagent-boundaries`.
- Workers must not edit shared registry, root planning files, or other workers' files unless the line card explicitly grants ownership.
- Never ask an existing worker to edit a different worktree than its actual cwd. If cwd, branch, thread, or registry ownership drift is unclear, preserve evidence and recommend archive + restart.

## Default Model

Use personal terms, not Trellis tool terms:

- `Line / Stage`: a bounded stream of work similar to a Trellis issue lifecycle.
- `Checkpoint`: a gate summary written only at major transitions.
- `Decision Record`: a compact trace of a state-changing decision, evidence paths, rationale, and outcome.
- `Recovery Queue`: recoverable stale, blocked, abandoned, or no-go work with revive conditions.
- `Finish Candidate`: a line that passed worker verification and coordinator intake, ready to route into branch finish.

Do not assume Trellis CLI, Trellis MCP tools, `.trellis/`, graph VCS state, or semantic AST diffs unless the user explicitly requests Trellis.

## Safety Defaults

- Active lines that edit files, run long jobs, or use workers require canonical worktrees.
- No line may start or continue without a Line Card.
- A line may enter `finish_candidate` only after `pass`, complete handoff, verification evidence, and coordinator intake.
- Do not auto-monitor long jobs; register long-job lines here and route monitoring details to the existing long-running job and subagent-boundary rules.
- Do not auto-merge, commit, create PRs, or mark project success from this skill. Route finish work to `personal-branch-finish` after the finish gate.
