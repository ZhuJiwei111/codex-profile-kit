---
name: supervise-long-jobs
description: Launch and supervise an already-authorized non-interactive local or SSH remote Linux, macOS, or Windows command expected to run longer than about ten minutes when the current Codex task should resume after completion, failure, a declared stage change, or a health condition. Use detached worker-side observation instead of model polling, Scheduled tasks, Stop hooks, or ad hoc terminals. Also use to discover monitor capabilities, reconnect to, acknowledge, or clean registrations created by this supervisor. Do not use for interactive commands, short commands, unauthorized resource use, experiment orchestration, or automatic cancellation, retry, restart, signaling, or reconfiguration.
---

# Supervise Long Jobs

Keep execution, sampling, and logs in the detached worker. Wait for durable job events without model polling; user messages and authorized coordination remain reasons to resume the conversation.

## Observation Scope And Ownership

Observe the registered command and its declared monitors on the assigned host,
GPU scope and artifact filesystems. Registration does not supervise every process
on a node, all project stages, App message delivery, or scientific correctness.
State what this command covers (for example, generation only, or an existing
pipeline that awaits generation and scoring) and what remains with its owner.
A launcher that exits after dispatching children does not prove those children
finished; choose the actual authorized command that waits for the intended work.

The task owner validates outputs and continues already-authorized stages; the
plugin reports runtime events. A completed stage is not completion of the user's
whole task, nor a reason to ask again for existing authority. Research changes
and additional experiments retain their own decision boundaries.

## Choose The Observation Contract

Resolve `<plugin-root>` as the directory two levels above this `SKILL.md`. Do not assume a home directory, clone path, mount, container layout, GPU index, or marketplace cache path.

Discover capabilities on the execution host before selecting health monitors. For SSH jobs use the remote adapter’s `capabilities` command. For local jobs call `get_capabilities()`. When local MCP is unavailable,
run the following with the current host's absolute Python runtime:

```text
<absolute-python-runtime> <plugin-root>/scripts/supervisor.py capabilities
```

Before launch, briefly state the command's stage/deliverable, baseline plus
selected monitors, and estimated duration and completion window. Use measured
progress/throughput when available, otherwise comparable work or an explicitly
labeled planning estimate. Estimates are not execution gates or fixed budgets.

For every ETA report (launch, reconnect, or progress update), name the estimated
stage or deliverable and give both remaining duration and the corresponding
clock time. Read the current clock when calculating it; use the user's timezone,
not the execution host's. Include the date when crossing midnight or otherwise
ambiguous. For example, if observed at `11 月 20 日 00:30（北京时间）`:
`阶段一预计还需 1.5–2 小时，预计 11 月 20 日 02:00–02:30 完成；后续 DMD 阶段尚无吞吐估计。`
Use ranges when appropriate, without implying a precise deadline. Do not repeat
an old remaining duration or completion window as current without checking its
basis. If the duration or current clock cannot be established, say which is
unavailable instead of inventing a time. A stage ETA is not the whole-job ETA.

- Baseline PID/start identity and atomic terminal result are always active on Linux, macOS, and Windows.
- For an ML job assigned NVIDIA GPUs on Linux, default to per-process-tree utilization below 5 percent for 15 minutes, with a 5-minute startup grace. Alert when utilization attributable to the target process tree stays below the threshold on any assigned GPU.
- For an ML output or artifact filesystem, pass an explicit disk monitor for available space below 5 percent or 20 GiB for 60 seconds. Use `--artifact` to record output paths and `--monitor` with `disk_free` to enable the alert.
- Add heartbeat only when the launched job explicitly owns and updates that path.

Derive GPU scope and filesystem paths from the authorized task and current capability result. In containers, enable process-attributed GPU monitoring only with evidence that driver PIDs and procfs target identities are comparable; capability discovery alone does not verify that mapping. If this is unknown, omit the default GPU monitor and report the evidence gap while retaining baseline and other supported monitors. If a context-aware default is unsupported, omit it and report the capability `evidence_gap`. If the user explicitly requires an unsupported monitor, stop before launch. Read [observation contract schemas](references/observation-contracts.md) when constructing monitor JSON.

## Launch

Confirm the command, working directory, resource use, and expected duration are already authorized. Use an absolute executable path and keep credentials out of command arguments.

```text
<absolute-python-runtime> <plugin-root>/scripts/supervisor.py \
  start --name <name> --cwd <absolute-cwd> \
  [--artifact <absolute-path>]... \
  [--stage-path <task-owned-snapshot>] \
  [--monitor '<strict-json-object>']... \
  -- <absolute-executable> <args>...
```

The detached worker records its own identity, launches the target with `Popen`, records the target identity separately, and samples the declared monitors while the target runs. Preserve the returned `job_id`. Terminal success or failure comes from the atomic result record, never PID disappearance alone.

## Reporting And Stage Changes

Identify work in user updates by task and stage. Keep supervisor job and event IDs internal unless the user requests them.

- **Launch / first wait:** give the scope and ETA before launch. Reuse that report at the first wait when both still apply.
- **Reconnect or requested status:** inspect the existing job and relevant current
  evidence; report the actual stage, observation time, progress and remaining ETA.
  A brief wait interruption with no changed facts needs no repeated status report.
- **Observed stage transition or material change:** explain what finished, what is
  now running or blocked, and the updated ETA/basis. A health event warrants a
  concise diagnosis and action or decision, not a declaration of failure by default.
- **Terminal result:** report this command's outcome and actual duration, distinguish
  output validation from runtime completion, and continue remaining authorized work.

For an authorized pipeline with meaningful internal stages, use its native current
stage record with `--stage-path`; when it has none, its existing coordinator may
publish a small atomic snapshot. Read the [stage snapshot interface](references/observation-contracts.md#stage-snapshot)
when wiring this input. The task defines stages and facts; the worker emits durable
nonterminal `stage_changed` events through the existing wait path. Without this
input, stage reporting is limited to evidence available at normal execution or
message boundaries. Existing jobs are not hot-reconfigured.

On a stage event, inspect the latest job state before reporting: a queued transition
may already have been followed by failure or completion. Report the current outcome,
with prior stages as context. Combine pending transitions into one current update, omit facts already reported, and acknowledge each consumed event. Do not label entry into a stage as its
successful completion. Sampling may miss short-lived overwritten snapshots, and
App exit or sleep delays conversation delivery; this is not periodic progress
notification. Ordinary increments stay in native records, not a second ledger.

If the owner launches separate authorized stages, each actual command has its own
registration; update the current execution pointer in the existing task record.
If the same command advances internally, retain its job ID. Reconsider monitors
for a new command's real resource scope; do not reuse a GPU assumption for a CPU
stage. Do not hot-reconfigure a running registration. Explain changed coverage
when relevant, and handle expected phase behavior as context rather than inventing
failures. Stage ETA, whole-task ETA and resource-release time are distinct; report
only what the evidence supports. Sharing reports with other chats follows
`personal-multiline-coordination`, not automatic event forwarding.

## Wait And Resume

Enter the native wait after the applicable scope/ETA report above. Resume the
same registration after message handling when its observation is still needed.

Call `wait_event(job_id)` for one job or `wait_any(job_ids)` for several. The host waits without model sampling and returns one unacknowledged `completed`, `failed`, `stage_changed`, `attention`, or `supervisor_error`, preserving its original job and event IDs. No event is automatically acknowledged. In a multi-job wait, closed observations are skipped; when all are closed and no event is pending, waiting ends with an error instead of hanging.

Do not supervise a waiting script or layer Goal polling, Scheduled tasks, shell polling, or another monitor around these waits. A finite command ends on its result. A resident public observer may wait indefinitely for a declared actionable condition: define what it observes, who handles events, and when its ownership ends. Normal waiting is not abandonment and does not justify a duplicate task.

When an event arrives:

1. Treat `attention` as a request to diagnose, not proof of failure.
2. Use the bounded event and `inspect_job(job_id)` first. If evidence remains insufficient, start with a small tail of the reported `combined.log` (normally up to 8 KiB). If insufficient, read the relevant error or stage region selectively; do not ingest the whole log by default.
3. Repair only when the original task already authorized that exact class of change. The event itself grants no new authority.
4. For `completed` or `failed`, calculate the supervisor wall-clock duration from the registration `created_at` in the reported `paths.job_dir/job.json` to the terminal `finished_at`. Include it in the first user-visible terminal report in the user's language, for example: `实际工作时间：2 小时 17 分`. If either timestamp is unavailable, report the closest labeled approximation or state why the exact duration is unavailable; never omit the actual-time line.
5. Acknowledgment means the runtime notification was consumed, not that scientific results were adopted. Keep remaining work with its existing owner and task records. Call `ack_event(job_id, event_id)` after consuming the event, then wait again only if observation remains viable (`inspect_job` reports `waitable`). A consumed `supervisor_error` with an inactive worker closes observation; inspect the target separately before deciding its outcome.

The plugin observes jobs and controls waits; it never controls workers, retries work, or schedules later stages. Events grant no new authority. The task owner may use other tools to act within existing task authorization; unrelated or expanded actions still need matching authority.

## Messages During A Wait

The plugin observes commands, not App chats or their message queues. Native chat
messaging and observation belong to `personal-multiline-coordination`. A successful
send confirms submission, not that the receiving model has read or acted on it.

For an authorized notification that needs handling now, send it through the
native chat tool and look for its corresponding reply or action. An `active`
status or unrelated commentary is not evidence of handling. If it is unhandled
and current evidence indicates a supervisor wait, resolve its job ID from the
active wait call or the owning task’s current execution record, then
call `interrupt_wait(job_id)` without another permission request. Do not guess a
missing/stale ID. An idle chat or an already handled message needs no interruption.
This releases the wait, not the job; do not acknowledge another owner's events
or restart its execution.

Confirm handling through native chat observation as described in
`personal-multiline-coordination`. Even a timed-out `wait_threads` snapshot may
contain the corresponding reply or action. If handling remains unconfirmed,
report the specific gap.

On `wait interrupted` (including a remote error wrapped as `SSH request failed`),
client cancellation, or incoming user input, handle the available message before
entering another wait. A released wait is not a failed
job or permission to relaunch it. Retain the existing job ID and resume observation
after handling the request when the task still calls for it. If no message is
visible, state that limitation rather than inventing an instruction. Do not add
periodic wakeups, message polling, or a second observer to keep chats responsive.

## Reconnect And Maintain

After App or MCP restart, use `list_jobs()` or `inspect_job(job_id)`. Worker-side health sampling continues while MCP is disconnected, and an unacknowledged disk event returns immediately after reconnect.

MCP client cancellation releases only its request. When a wait must be released through another available caller, use `interrupt_wait(job_id)`: existing waits watching that job, including multi-job waits and other MCP instances sharing the state directory, exit at their next observation cycle. Later waits are unaffected. The response confirms an interruption request, not that a waiter existed. Workers, targets and pending events remain unchanged. Waits started by older plugin code do not observe this control; upgrade the waiting client at an idle boundary without restarting healthy workers. This does not guarantee that the App dispatches a new message while a tool is blocked.

If MCP reports `Transport closed`, preserve the job IDs and use available inspection or CLI recovery. Reconnect when the host supports it; use a fresh task only when the current transport cannot recover and task creation is authorized. Do not repeatedly call a known-dead transport or relaunch a healthy job.

CLI fallbacks are:

```text
<absolute-python-runtime> <plugin-root>/scripts/supervisor.py list
<absolute-python-runtime> <plugin-root>/scripts/supervisor.py status JOB_ID
<absolute-python-runtime> <plugin-root>/scripts/supervisor.py ack JOB_ID EVENT_ID
<absolute-python-runtime> <plugin-root>/scripts/supervisor.py interrupt-wait JOB_ID
<absolute-python-runtime> <plugin-root>/scripts/supervisor.py clean JOB_ID
```

Ordinary `clean` requires an inactive worker, no known live target, and an acknowledged target result or confirmed failure to create the worker. An observation error alone leaves the records available for diagnosis. For a confirmed released SSH host, use the separate cleanup procedure in [remote access](references/remote-access.md).

## SSH Remote Jobs

Use the same detached worker and native event store on the remote host. Read
[remote access](references/remote-access.md) for connection fields and commands.
Remote capability discovery runs on the execution host; the MCP capability tool
still describes the controller. Existing MCP inspect, wait, interrupt, list, and
ack tools route registered remote job IDs automatically.

An uncertain SSH response does not authorize a second execution. Preserve the
reserved job ID and reconnect with it. App exit, local sleep, or SSH loss leaves
the remote worker running; the controller consumes persistent events when it
returns. This is not an offline AI takeover or a guarantee of App notification.
A released container loses its processes; shared records support inspection and
an explicitly authorized recovery, not automatic restart. Any remote AI worker requires an explicit delegation.
