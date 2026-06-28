---
name: personal-long-job-status
description: "Use only when the user explicitly invokes $personal-long-job-status or explicitly asks to apply this skill to check current task or job status and ETA, in either a main conversation or side conversation. Manual one-shot status checks only: prefer known local long-running jobs when visible; otherwise report the current Codex task status. Do not use implicitly when launching jobs, and do not use for automatic monitoring, general debugging, CI fixes, tests, normal command output, or unstated status curiosity."
---

# Personal Long Job Status

## Purpose

Check the current task or a known local long-running job without taking ownership of continuous monitoring. Prefer visible local job evidence such as a command, PID, session, log, output directory, artifact, or terminal output. If no specific job is visible, report the current Codex conversation task status, likely next step, blocking state, and ETA.

## Rules

- Use only low or medium reasoning effort for this skill. If the runtime or delegated side conversation can choose reasoning effort, prefer low; use medium only when sparse evidence requires ETA inference. Do not use high, xhigh, or equivalent high-effort modes for this skill.
- Stay read-only unless the user explicitly asks for a mutation after invoking this skill.
- Do not stop, restart, kill, re-run, or parallelize the job.
- Do not tail logs continuously or enter polling loops.
- In side conversations, when a parent-thread job is identified by PID, session id, command, output path, or task name, a single bounded process-liveness check is allowed. If sandboxed `ps` or terminal access cannot see the parent process, request the narrowest necessary permission to check that specific PID or command; do not broaden into system-wide process discovery.
- Prefer one bounded status pass, then report.
- If a job is still running, estimate remaining time and exit the conversation.
- If a job has completed, summarize completion evidence and suggest only minimal read-only verification commands. Do not run verification unless the user explicitly asks.
- Avoid printing secrets from commands, logs, environment, or config.
- When inspecting logs, summarize safe evidence such as timestamps, counts, milestones, or non-sensitive status lines. Do not paste suspicious or sensitive log text verbatim.
- Do not offer continuous monitoring unless the user explicitly asked for it.

## Context Boundary

Use only context that is already visible or explicitly provided:

- Current conversation context and current terminal output.
- User-provided command, cwd, PID, session id, log path, output path, artifact path, or task name.
- Known artifacts or paths already established in the conversation.

Do not broadly scan the system, repository, home directory, process table, or logs to guess which task the user means. If the relevant task cannot be identified, report status as `unknown` and ask for the smallest useful clue for a later check: command, cwd, PID/session id, log path, output path, or task name.

## Status Pass

For a known local job, collect only the facts needed for ETA and handoff:

- Current time and timezone.
- Original command, cwd, session id, PID, log path, output path, or artifact path from conversation context.
- Whether the job is still running, completed, failed, or unknown.
- Latest artifact progress from file counts, manifest state, output mtimes, log tail, or scheduler status.
- Rate estimate from recent artifacts or log milestones.
- Expected completion condition, such as final manifest row count, expected output files, success marker, process exit, or known final log line.

Use local, bounded, read-only commands. Examples:

```bash
date '+%F %T %Z'
ps -o pid,etime,pcpu,pmem,rss,args -p <pid>
pgrep -af -- <known-command-fragment>
find <output-dir> -maxdepth 1 -type f -printf '%T@ %p\n' | sort -n | tail -20
tail -n 80 <log-file>
```

For shell-session jobs without a visible PID, inspect only available session output or artifacts. Do not infer that a process is gone solely because a sandboxed `ps` cannot see it. In side conversations, if the job is known but process visibility is blocked by sandbox isolation, report `unknown` unless the user has allowed a narrow process-liveness check outside the sandbox.

For current Codex task status when no local job is visible, use conversation state instead of local probing:

- Current phase or action.
- Completed work and remaining work.
- Known blockers or missing inputs.
- Expected next step and rough completion time.

## ETA Method

- Prefer progress-unit estimates over CPU time: completed shards, files, rows, epochs, batches, samples, or log milestones.
- Use recent rate when available; otherwise use whole-run average.
- State uncertainty plainly when source sizes vary or the rate is noisy.
- Include both a best estimate and a conservative bound when possible.
- If progress cannot be measured, report what is known and give the next safe check command instead of inventing an ETA.

## Response Shape

Keep the answer short and actionable:

- Status: running, completed, failed, blocked, or unknown.
- Evidence: one or two concrete facts with timestamps, counts, latest artifact names, or conversation-state facts.
- ETA: estimated remaining time, or `unknown` with uncertainty.
- Handoff: known command, cwd, session/PID, log/output path, and the next check to run.
- Next step: if a job is still running, tell the user this bounded check is complete; if this is current Codex task status, state the next work item and rough completion window.

If there is not enough information to identify a side-conversation task, report `unknown` and name the minimum clue needed for the next status check.
