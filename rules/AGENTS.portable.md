# Portable Codex Instructions

These are durable, machine-neutral instructions for Codex sessions. Keep
host-specific facts in `HOST_LOCAL.md`, not in this file. Project repositories
may add narrower `AGENTS.md` files.

## Maintenance

- Keep this file short, durable, and behavior-focused.
- Store only long-lived preferences here; exclude task notes, logs, temporary
  state, and long explanations.
- Write Codex-facing instructions in English unless the user explicitly asks
  otherwise.


## Workflow

- Keep context short. Prefer fast, bounded local inspection over broad scans,
  large file dumps, or unbounded logs.
- In unfamiliar repositories, do only enough intake to identify the edit
  surface, commands, verification path, and user changes.
- Check `git status --short` before broad edits. Never revert unrelated user
  changes unless explicitly requested.
- Prefer `apply_patch` for small manual edits. For whole-file generation, large
  mechanical rewrites, or formatting-driven changes, use the safest appropriate
  tool, then inspect the diff or resulting file.
- For one-off checks, statistics, artifact migrations, post-processing, or other
  temporary needs that are not part of the project's durable behavior, prefer
  temporary helper scripts over adding branches, flags, or special cases to
  production code. Keep production changes focused on reusable behavior, and use
  direct artifact transformation when it is cheaper and semantically safe.
- For temporary helper code and artifacts, follow `Temporary Workspaces` below:
  preserve traceable helpers and evidence, but clean pure throwaway or sensitive
  material.
- Do not use Python or other scripts to generate final Markdown prose by
  default. Use scripts to collect structured evidence such as CSV, JSON, TSV,
  logs, counts, or metrics when helpful, then write the Markdown document
  directly as human-readable Codex-authored prose grounded in that evidence.
- Script-generated Markdown is only appropriate for mechanical artifacts such as
  large tables, indexes, API reference dumps, or explicitly requested
  reproducible reports. State that tradeoff before using a generator.
- The user welcomes questions and targeted help requests. When ambiguity affects
  correctness, scope, data safety, cost, environment choice, output format, or
  user-visible behavior, ask the user instead of guessing or inventing defaults.
  Make small local choices independently when they are low-risk and easy to
  adjust, and mention the assumption when useful.
- When asking non-blocking questions, prefer a Plan-mode style choice prompt:
  present 2-3 concrete options, put the recommended default first, explain the
  tradeoff briefly, and continue with the safe default when possible for
  plain-text prompts. When using `request_user_input`, do not set
  `autoResolutionMs` by default; multiple-choice prompts should wait
  indefinitely for the user's reply. Use auto-resolution only when the user
  explicitly allows it.
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
  narrowest appropriate scope. Change global configuration only when explicitly
  requested or clearly part of the task.
- When completing a task, suggest concise next-step commands or prompts only
  when they directly help; skip generic follow-ups.


## Long-Running Jobs

- Short tasks expected to finish within 10 minutes may be monitored, tailed, or
  awaited to completion when that helps finish and verify the work.
- Treat jobs expected to run longer than 10 minutes as long-running jobs. This
  includes GPU training, experiments, batch processing, large downloads, model
  conversion, evaluation runs, and anything the user explicitly calls
  long-running.
- By default, start long-running jobs detached with `tmux` or `nohup` instead of
  keeping them attached to a Codex tool session. Use `tmux` when reattachment or
  interaction matters, and `nohup` for simple one-command runs.
- For planned or long-running work, treat approved plan names, stages,
  artifacts, and success criteria as execution contracts. Before launch, state
  any Plan vs Actual mapping for commands, output paths, logs, session names,
  and expected artifacts.
- Do not introduce new user-visible phase names, output layouts, or status terms
  without reporting the mapping first. If aliases are useful, keep the planned
  name first, such as `Stage1B/Round1`.
- The main process may run a bounded startup guard for long-running jobs without
  separate active-monitoring authorization. This is startup validation, not
  long-term monitoring. Keep it read-only and capped at 10 minutes total, which
  may include launch confirmation, process/session liveness, log creation,
  output directory writability, expected first progress signal, and a few bounded
  GPU/status samples when relevant.
- During the startup guard, treat immediate failures, missing expected launch
  evidence, no first progress signal after the agreed warmup, obvious resource
  errors, or unexplained GPU abnormalities as startup anomalies. Report the
  evidence and either stop for user guidance or hand off with the anomaly clearly
  marked; do not silently keep waiting past the 10-minute cap.
- Without explicit current-stage active-monitoring authorization, estimate
  runtime, launch only if appropriate, run at most the bounded startup guard,
  then hand off the command, cwd, environment, session or PID, log path, output
  path, expected artifacts, one status-check command, startup guard result, and
  success/failure signals. Then end the current turn and wait for the user to
  return for result inspection or analysis.
- The main process must not monitor long-running jobs by repeatedly polling,
  repeatedly tailing logs, running `tail -f`, running `watch`, running
  `watch nvidia-smi`, running `nvidia-smi -l`, using `while true`, looping on
  `ps`, reading logs in a loop, polling artifacts, polling GPU status, keeping
  a terminal open for observation, or spawning watcher agents unless the user
  explicitly authorizes active monitoring for the current stage.
- Only when the user explicitly authorizes active monitoring for the current
  stage may the main process spawn a monitoring subAgent after launch or startup
  guard. The main process must state the Plan vs Actual mapping for command,
  cwd, environment, session or PID, log path, output path, expected artifacts,
  monitoring record path, event triggers, and any preapproved next actions.
- Before spawning a monitoring subAgent, define an inline monitoring contract.
  The contract must include `job_id`, `phase`, `permission_scope`, `cwd`,
  `command`, `session_or_pid`, `log_path`, `output_path`, `expected_artifacts`,
  `startup_guard_result`, `health_signals`, `job_specific_thresholds`,
  `fallback_thresholds`, `cadence`, `record_path`, `event_triggers`,
  `read_only_diagnostics`, `forbidden_actions`, `stop_or_timeout_condition`,
  `report_format`, and `preapproved_next_actions`.
- Prefer job-specific health signals and thresholds whenever the command,
  framework, logs, or plan make them knowable. If the contract does not define a
  relevant threshold, apply conservative fallback checks for process/session
  anomalies, stalled progress, GPU anomalies, resource pressure, error signals,
  and result or metric anomalies.
- With authorized active monitoring, the main Codex turn becomes a persistent
  supervisor. Spawn a monitoring subAgent with the lowest available reasoning
  effort, then use repeat long wait with the longest available sleep or wait for
  monitoring subAgent events. If a wait times out without an event, continue
  waiting; do not exit, inspect logs, poll artifacts, query GPU status, or take
  over monitoring just because the wait expired.
- The read-only restriction is monitoring subAgent only. A monitoring subAgent
  may inspect status and write compact monitoring records, but it must not stop,
  restart, repair, launch the next stage, publish, clean artifacts, mutate
  training outputs, or make go/no-go decisions.
- Other subagents, including explorer, worker, editing, and validation
  subagents, are not limited by the monitoring read-only rule. They follow the
  normal delegated ownership, exclusive-file, command, edit, and verification
  rules for their task.
- The low-reasoning restriction is also monitoring subAgent only. Keep the
  inherited/default model unless the user asks otherwise, and do not switch the
  monitoring model unless the user explicitly asks. Set the monitoring
  subAgent's reasoning effort to the lowest available option when the runtime
  supports it. Other subagents may use the reasoning effort appropriate to their
  delegated task.
- Use dynamic sparse cadence instead of a fixed cadence. Before spawning a
  monitoring subAgent, estimate cadence from the total runtime, first visible
  progress point, likely early-failure window, artifact or log update cadence,
  and preapproved next-stage trigger. Choose sparse checks from that estimate:
  30-60 minutes for shorter jobs, first check after 45-60 minutes for multi-hour
  jobs then 90-120 minutes once stable, and 2-4 hours for stable overnight or
  multi-day jobs. If early-failure risk is high, shorten only the first check
  and then back off.
- Cadence is not a reason to ignore anomalies. At each monitoring check, the
  monitoring subAgent must compare current evidence with the contract's
  job-specific thresholds first, then fallback thresholds. If an anomaly is
  detected, return an `action_needed` event with a compact read-only diagnostic
  summary instead of sleeping until the next cadence.
- Fallback process/session anomalies include a missing tmux session or PID,
  defunct process, command mismatch, target child process exit, or a live wrapper
  whose expected worker process is gone.
- Fallback stalled-progress anomalies include no log growth, no step/epoch/sample
  progress, unchanged expected artifacts or checkpoints, missing first artifact
  after warmup, or an ETA that cannot be supported by observable progress.
- Fallback GPU anomalies include sustained low utilization after warmup,
  repeated low/high utilization thrashing such as unexplained 0-100 swings,
  wrong or missing expected device use, multi-device imbalance only when the
  contract says the job should use balanced devices, and GPU memory or CUDA
  errors. Non-target processes on the same GPU are background context only; do
  not treat shared GPU occupancy as an anomaly by itself.
- Fallback resource-pressure anomalies include low disk space or inodes, RAM or
  swap pressure, insufficient `/dev/shm`, high IO wait that explains a stall,
  write-permission failures, or filesystem errors.
- Fallback error-signal anomalies include repeated or fatal log signatures such
  as OOM, CUDA/NCCL failures, segmentation faults, tracebacks, data loader
  errors, permission denied, no space left, connection reset, or missing input
  data.
- Fallback result or metric anomalies include `nan` or `inf` metrics, sudden
  throughput collapse, ETA regression without progress explanation, zero-byte
  checkpoints, or outputs stuck in temporary or partial-file states.
- Monitoring subagents are read-only observers of the monitored job. During
  normal progress they update compact status files and keep sleeping. They
  should return a short event summary to the persistent supervisor only for
  `action_needed`, `failed`, `completed`, `preapproved_next_ready`, or an agreed
  milestone.
- Use `action_needed` for anomalies that require user or supervisor judgment,
  `failed` only when failure is directly evidenced by process exit, fatal logs,
  or contract-defined failure markers, `completed` only when the completion
  condition is evidenced, and `preapproved_next_ready` only when the contract's
  preapproved next-step trigger is satisfied.
- Monitoring records default to the project `.codex/monitoring/<job-id>/`
  directory. Use `monitor_status.json` for compact machine state and
  `monitor_report.md` for a short human-readable report.
- `monitor_status.json` must include at least `job_id`, `phase`,
  `permission_scope`, `status`, `updated_at`, `cwd`, `command`,
  `session_or_pid`, `log_path`, `output_path`, `latest_check`, `progress`,
  `eta`, `signals`, `stop_reason`, and `next_safe_action`.
- Do not copy long logs or secrets into monitoring artifacts.
- For monitoring records and reports, write `updated_at`, `latest_check`,
  `eta`, handoff times, and subAgent status messages in Asia/Shanghai time
  (UTC+8) by default. Preserve UTC only when quoting external logs or
  artifacts, and label it explicitly.
- Preserve handoff context: command, cwd, environment, tmux session or nohup
  process id, log path, output path, estimated completion time, one status-check
  command, expected artifacts, and success/failure signals for later audit.
- When the main process receives a monitoring subAgent event, the persistent
  supervisor may execute a repair, restart, or next step only if that action was
  already preapproved in the plan. Ask first for unapproved actions, scope
  changes, data-safety choices, environment changes, heavy resource use, or
  cost-impacting work.
- Outside explicitly authorized active monitoring, do not proactively audit
  results. Wait for the user to return after completion and ask for result
  inspection or analysis.


## Language

- Use Chinese by default for all user-visible prose, including final answers,
  plans, experiment designs, implementation plans, reports, handoffs, summaries,
  generated documents, and code comments when practical.
- Use Chinese section titles and headings in user-visible plans and reports. Do
  not keep English template labels from skills when a natural Chinese label is
  available.
- Preserve English only for commands, paths, filenames, code identifiers, API
  names, model or environment names, metric keys, quoted source text, and
  external artifacts whose established convention is English.
- Use English for Codex-facing artifacts such as `AGENTS.md`, `SKILL.md`,
  plugin metadata, and internal workflow or configuration notes.
- When an artifact could be either user-facing or Codex-facing, treat it as
  user-facing if the user will read it as the deliverable; mention any
  English-only exception explicitly.
- User-visible plans, implementation plans, handoff summaries, and review notes
  are user-facing even when they describe creating or editing Codex-facing
  artifacts. Write the surrounding explanation in Chinese, while keeping the
  Codex-facing artifact content itself in English when appropriate.
- Follow established language conventions for external artifacts unless the
  user overrides them.


## Temporary Workspaces

- Put temporary helper code under the relevant directory's `tmp/` folder by
  default when it provides useful traceability, and mention the path in the
  handoff.
- Preserve small helper scripts or evidence files when they document how
  structured evidence was produced. Remove them only when explicitly asked or
  when they contain sensitive data.
- After a task is completed and verified, remove throwaway helper directories,
  caches, and intermediate artifacts that have no audit value, unless the user
  asks to keep them.
- Do not write sensitive data into temporary artifacts. If sensitive temporary
  data is unavoidable, avoid logging it and clean it up before handoff.


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

- Never print, copy, or write secrets into logs, reports, commits, `AGENTS.md`,
  `SKILL.md`, Hookify rules, or other durable rule files.
- Treat tokens, API keys, passwords, cookies, private keys, authenticated proxy
  URLs, `.netrc`, `~/.secrets/env`, other secret environment files, SSH private
  keys, and Codex auth files as sensitive.
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
  engineering. The user is happy to answer clarifying questions; prefer asking
  over making fragile assumptions.
