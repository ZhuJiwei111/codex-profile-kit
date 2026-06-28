# Portable Codex Instructions

These are durable, machine-neutral instructions for Codex sessions. Keep
host-specific facts in `HOST_LOCAL.md`, not in this file. Project repositories
may add narrower `AGENTS.md` files.

## Workflow

- Keep context short. Prefer fast, bounded local inspection over broad scans,
  large file dumps, or unbounded logs.
- In unfamiliar repositories, do only enough intake to identify the edit
  surface, commands, verification path, and user changes.
- Check `git status --short` before broad edits in a git repository.
- Never revert unrelated user changes unless explicitly requested.
- Prefer `apply_patch` for small manual edits. For whole-file generation, large
  mechanical rewrites, or formatting-driven changes, use the safest appropriate
  tool, then inspect the diff or resulting file.
- For one-off checks, statistics, artifact migrations, post-processing, or
  temporary needs, prefer temporary helper scripts over adding production flags
  or special cases.
- Do not use scripts to generate final Markdown prose by default. Use scripts
  for structured evidence such as CSV, JSON, TSV, logs, counts, or metrics, then
  write final prose directly.
- Ask targeted questions when ambiguity affects correctness, scope, data
  safety, cost, environment choice, output format, or user-visible behavior.
- When asking non-blocking questions, prefer a Plan-mode style choice prompt:
  present 2-3 concrete options, put the recommended default first, explain the
  tradeoff briefly, and continue with the safe default when possible instead of
  stopping the answer.
- When using `request_user_input`, do not set `autoResolutionMs` by default.
  Multiple-choice prompts should wait indefinitely for the user's reply. Use
  auto-resolution only when the user explicitly allows it.
- Treat user phrases such as `我的concern`, `讨论`, `不是命令`,
  `不一定要按我的`, `你觉得呢`, or similar uncertainty markers as discussion
  signals. In that mode, do not mechanically execute the user's provisional
  idea: first reason about it, explain tradeoffs, offer recommendations, and
  push back when the proposal seems risky or misaligned.
- Use the same discussion-first posture for high-ambiguity or high-risk work
  such as research direction, complex refactors, data-production strategy,
  long-running jobs, destructive changes, or unclear acceptance criteria.
  Simple explicit commands should still be handled directly without ceremony.
- If a prompt mixes discussion signals with an implementation request, first
  convert the concern into a short plan, risk list, or locked assumptions. Ask
  one targeted question when execution intent or acceptance criteria remain
  unclear.
- After repeated failures, summarize the lesson and put durable guidance in the
  narrowest appropriate scope.
- When completing a task, suggest concise next-step commands or prompts only
  when they directly help.


## Long-Running Jobs

- Short tasks expected to finish within 10 minutes may be monitored, tailed, or
  awaited to completion when that helps finish and verify the work.
- Treat jobs expected to run longer than 10 minutes as long-running jobs,
  including GPU training, experiments, batch processing, large downloads, model
  conversion, evaluation runs, and anything the user calls long-running.
- Start long-running jobs detached with `tmux` or `nohup` by default.
- Without explicit current-stage active monitoring authorization, do at most one
  immediate read-only sanity check, hand off the command, cwd, environment,
  session or PID, log path, output path, expected artifacts, and one
  status-check command, then end the current turn and wait for the user to
  return for result inspection or analysis.
- The main process must not monitor long-running jobs by repeatedly polling,
  repeatedly tailing logs, running `tail -f`, running `watch`, running
  `watch nvidia-smi`, running `nvidia-smi -l`, using `while true`, reading logs
  in a loop, polling artifacts, or keeping a terminal open for observation.
- Only when the user explicitly authorizes active monitoring for the current
  stage may the main process spawn a monitoring subAgent. The main process must
  state the Plan vs Actual mapping for command, cwd, environment, session or PID,
  log path, output path, expected artifacts, monitoring record path, event
  triggers, and any preapproved next actions.
- With authorized active monitoring, the main process becomes a `persistent supervisor`.
  It uses repeat long wait by running the longest available
  sleep/wait for monitoring subAgent events. If a wait times out without an
  event, it continues waiting; it must not exit, take over monitoring, read
  logs, poll artifacts, or query GPU status itself.
- monitoring subAgent only is a read-only observer. It may inspect status and
  write compact monitoring records, but it must not stop, restart, repair,
  launch the next stage, publish, clean artifacts, mutate training outputs, or
  make go/no-go decisions.
- Other subagents, including explorer, worker, editing, and validation
  subAgents, are not limited by the monitoring read-only rule; they follow the
  normal delegated ownership, exclusive-file, command, edit, and verification
  rules for their task.
- A monitoring subAgent should use low reasoning only. If the runtime supports
  `reasoning_effort`, set it to `low`; otherwise use `lowest available reasoning effort`.
  Do not change reasoning effort for ordinary subAgents, and do not switch the
  monitoring model unless the user explicitly asks.
- A monitoring subAgent normally updates status files and sleeps. It should
  return a short event summary to the main process only for `action_needed`,
  `failed`, `completed`, `preapproved_next_ready`, or an agreed milestone.
- Monitoring artifacts default to the project-local
  `.codex/monitoring/<job-id>/` directory. Use `monitor_status.json` for compact
  machine state and `monitor_report.md` for a short human-readable report.
- `monitor_status.json` must include at least `job_id`, `phase`,
  `permission_scope`, `status`, `updated_at`, `cwd`, `command`,
  `session_or_pid`, `log_path`, `output_path`, `latest_check`, `progress`,
  `eta`, `signals`, `stop_reason`, and `next_safe_action`.
- Do not copy long logs or secrets into monitoring artifacts.
- Use estimate cadence instead of a fixed cadence. Before monitoring starts,
  estimate total runtime, first visible progress point, early failure window,
  log or artifact update frequency, and next-stage trigger condition.
- Dynamic sparse cadence defaults: short tasks check every 30-60 minutes;
  multi-hour tasks first check after 45-60 minutes and back off to 90-120
  minutes when stable; overnight or multi-day tasks back off to every 2-4 hours
  when stable. If early failure risk is high, shorten the first check, then back
  off after stability is established.
- When the main process receives an event, it may continue with a repair,
  restart, or next step only if that action was preapproved in the plan. If the
  action is not preapproved, or if it affects cost, resources, data safety,
  environment configuration, or scope, ask the user first.
- Do not proactively audit results. Wait for the user to return and ask for
  result inspection or analysis.


## Language

- Use Chinese for user-facing replies, summaries, generated documents, and code
  comments when practical.
- Use English for Codex-facing artifacts such as `AGENTS.md`, `SKILL.md`,
  plugin metadata, and workflow notes.
- User-visible plans, implementation plans, handoff summaries, and review notes
  are user-facing even when they describe creating or editing Codex-facing
  artifacts. In those cases, write the surrounding explanation for the user in
  Chinese, while keeping the Codex-facing artifact content itself in English.
- Follow established language conventions for external artifacts unless the
  user overrides them.


## Temporary Workspaces

- Put temporary helper code under the relevant directory's `tmp/` folder by
  default, preserve it for traceability, and mention the path in the handoff.
  Remove it only when explicitly asked or when it contains sensitive data.


## Host Overlay

* Fill target-machine facts in `HOST_LOCAL.md` before relying on host-specific
  assumptions.
* Verify shell behavior, timezone, proxy commands, storage paths, GPU/CUDA
  availability, and preferred Python/Conda locations on the target machine.
* Prefer `python3` over `python` unless a conda or virtual environment is
  active.
* Verify less-common tools with `command -v` before relying on them.
* Do not assume a graphical editor command exists; prefer non-interactive
  commands.

## Python And Conda

* Keep the `base` conda environment minimal. Do not use `base` for project work
  and do not install project packages into `base`.
* Use project-specific environments. If the intended environment is unclear, ask
  before installing packages.
* Prefer `uv` for Python package and environment workflows when it fits the
  project, but do not mix it into an unclear conda setup without checking first.
* If a missing Python package would materially simplify the work, propose
  installing it in the correct project environment.
* Do not assume user-site Python packages are visible.

## Proxy And Network

* Avoid wasting proxy bandwidth. Before large downloads, datasets, models,
  wheels, archives, or other high-traffic operations, test direct access with a
  small request and prefer direct download when it works.
* Small metadata queries, package index checks, GitHub access, and external docs
  may use proxy when needed.
* Ask before running package-manager operations that may fetch large dependency
  trees.
* If unsure whether a high-traffic task should use proxy, ask first.

## Storage And GPU

* Check available storage before creating or downloading large artifacts.
* Check GPU availability before GPU work.
* Use explicit GPU device scoping for heavy GPU jobs and ask first before heavy
  GPU use.

## Security

- Never print, copy, or write secrets into logs, reports, commits, or durable
  rule files.
- Treat tokens, API keys, passwords, cookies, private keys, authenticated proxy
  URLs, `.netrc`, secret environment files, SSH private keys, and Codex auth
  files as sensitive.
- If a sensitive file must be inspected, report only the path, permission issue,
  or configuration category. Redact values as `<REDACTED>`.


## Ask First

- Ask before installing software, changing global or user-level configuration,
  running high-traffic network operations, touching credentials, launching
  long-running or heavy resource jobs, or taking destructive actions outside an
  explicitly approved scope.
- Ask for targeted user help when a short decision, path, credential approval,
  file, requirement, environment detail, library, preference, or tool choice
  would unblock the work faster and more safely than brittle reverse
  engineering.
