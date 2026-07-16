# Active Monitoring Protocol

Read this reference only after the user explicitly authorizes active monitoring
in the current Codex thread. It is not a trigger to create a watcher.

## Entry Gate

The durable long-running-work instructions own launch authorization, detached
execution, the bounded startup guard, and the handoff required when monitoring
is not authorized. This protocol consumes the startup result; it does not
extend or repeat the startup guard.

Before spawning or rearming a monitoring observer, confirm:

- the current Codex thread has explicit active-monitoring authorization, which
  the user has not narrowed or revoked;
- the job, phase, process or session, evidence paths, and completion condition
  are known;
- checks can remain read-only with respect to the job and its outputs;
- the observation target is classified by its actual evidence and impact
  surfaces, not only by the job label;
- the selected risk tier's read-only gate is satisfied and recorded; and
- the main process will remain responsible for judgment while the job-owning
  executor remains responsible for any separately authorized later action.

Thread-scoped authorization permits reuse of the monitoring capability without
another user prompt, but it does not carry a prior PID, cadence, evidence path,
or action authority into a new job. Create a fresh contract for every job or
phase and keep at most one observer on the same monitored job.

The default applicability is a `low-risk local long job`: local `Python
processing`, `download`, or `training` observed only through local process or
session state, logs, and outputs. When the live spawn surface cannot verify the
requested custom profile or effective sandbox, this tier may use
`read_only_enforcement: prompt_only`; the observer is allowed only when the
contract and user-visible launch disclosure also state
`profile_verification: profile_unverified`. Treat a download as low-risk only
when the observer never contacts the remote source, handles its credentials, or
mutates external state.

A sensitive, external, production, or high-impact target requires mechanical,
product-confirmed, or runtime-verified read-only enforcement. Neither
`prompt_only` nor a merely configured profile satisfies that elevated gate. If
the required enforcement cannot be demonstrated, record the gate as unavailable
and create no observer. Do not make the main process poll as a fallback.

## Monitoring Contract

Define this contract before delegation:

```yaml
monitoring:
  job_id:
  phase:
  permission_scope:
  authorization_scope: thread
  authorization_source:
  cwd:
  command:
  session_or_pid:
  log_path:
  output_path:
  expected_artifacts: []
  startup_guard_result:
  estimated_runtime:
  runtime_gate:
    target_class: low_risk_local | sensitive | external | production | high_impact
    rationale:
    decision: verified_read_only | disclosed_prompt_only | no_monitor
  execution_profile:
    requested_role: monitor
    requested_model: gpt-5.6-luna
    requested_reasoning_effort: high
    selection_mechanism: custom_agent | explicit_override | runtime_choice
    configuration_state: configured_unverified
    profile_verification: runtime_verified | profile_unverified
    read_only_enforcement: mechanical | product_confirmed | runtime_verified |
      prompt_only
    user_visible_disclosure:
    fallback: no_monitor
  health_signals: []
  job_specific_thresholds: []
  fallback_thresholds: []
  cadence:
  cadence_rationale:
  event_triggers: []
  read_only_diagnostics: []
  forbidden_actions: []
  stop_or_timeout_condition:
  report_format:
  durable_record:
    required: false
    path:
    writer:
  preapproved_next_actions: []
```

`preapproved_next_actions` lists actions the main process may later authorize
for the job-owning executor.
Preapproval does not authorize the monitoring observer to execute them. It does
not turn the main process into the substantive executor.

## Model And Reasoning Boundary

The configured `monitor` file requests `gpt-5.6-luna` at high reasoning effort
for bounded evidence synthesis while remaining a read-only observer. This is a
requested profile, not runtime proof. High reasoning does not authorize
diagnosis, mutation, or a stage decision, and the parent agent's current profile
is not the monitor's quality or cost baseline.

When a monitoring contract requires causal analysis that cannot be expressed as
bounded checks, hand it to a separately scoped diagnostic executor after main
intake. Do not change a running observer's model or reasoning effort. If the
work becomes diagnosis, emit
`需要处理` with internal `event_type: action_needed` and hand off to a
separately scoped diagnostic workflow.

## Cadence

The supervisor owns the cadence decision. Before delegation or rearming, it
estimates runtime and records a cadence rationale from the early failure window,
first visible progress point, log or artifact update frequency, expected
completion, and next meaningful evidence event. Do not require a fixed interval
when the job supplies better timing evidence.

- Prefer event-driven waits and sparse checks over polling loops.
- Check earlier only when startup risk remains material after the startup
  guard.
- Back off after stable evidence.
- Treat a cadence as too frequent when another check is unlikely to observe new
  evidence, and as too sparse when it can miss the relevant failure window or
  delay terminal evidence beyond the next useful decision point.
- Re-estimate only when observed throughput, progress, risk, or the expected
  completion time changes materially; do not shorten cadence merely because a
  timeout elapsed.
- Do not read logs, artifacts, process state, and GPU state merely because a
  wait timeout elapsed; perform the next contract-defined check.
- A sparse cadence never suppresses an anomaly found during an authorized
  check.

Do not encode one global numerical interval for all jobs. Record any numerical
cadence in the job contract where its rationale can be reviewed.

When the supervisor cannot derive a more meaningful event-based cadence, use
the legacy ranges only as non-binding sanity checks, never as a mandatory
schedule:

- shorter long-running jobs: check every 30-60 minutes;
- multi-hour jobs: first check after 45-60 minutes, then every 90-120 minutes
  after stable evidence; and
- stable overnight or multi-day jobs: check every 2-4 hours.

Shorten only the first fallback check when material early-failure risk remains
after the startup guard, then back off. Override these ranges whenever
job-specific signals justify a different cadence, record the rationale in the
contract, and let an earlier evidence event supersede the next scheduled check.
These ranges do not authorize extra polling.

## Health Signals And Fallback Anomalies

Use job-specific signals and thresholds first. When the contract does not cover
a relevant class, use conservative fallback checks:

- **Process or session:** missing session or PID, defunct process, command
  mismatch, target child exit, or a live wrapper with no expected worker.
- **Progress:** no expected log or artifact change, no step or sample progress,
  missing first artifact after the declared warmup, or an ETA unsupported by
  observable progress.
- **GPU:** wrong or missing expected device use, sustained low utilization after
  warmup, unexplained utilization thrashing, contract-relevant device
  imbalance, memory pressure, or CUDA/NCCL errors. Unrelated processes on a
  shared GPU are context, not failure by themselves.
- **Resources:** low disk space or inodes, RAM or swap pressure, insufficient
  shared memory, IO pressure explaining a stall, write-permission failures, or
  filesystem errors.
- **Errors:** fatal or repeated OOM, CUDA/NCCL failure, segmentation fault,
  traceback, data-loader failure, permission denied, no space left, connection
  reset, or missing input.
- **Results:** `nan` or `inf`, unexplained throughput collapse, zero-byte
  checkpoint, or output stuck in a temporary or partial state.

Return a compact evidence packet. Do not copy long logs, environment dumps,
credentials, authenticated URLs, or secret-bearing command output.

## Evidence Events

Write user-visible monitoring reports in Chinese. Use these non-authoritative
event names, with the English value retained only as an internal `event_type`
when machine-readable routing needs it:

- `里程碑` (`milestone`): a contract-defined progress boundary is evidenced;
- `需要处理` (`action_needed`): ambiguity or anomaly requires supervisor or
  user judgment;
- `失败证据` (`failure_evidence`): direct process, log, or contract-defined
  failure evidence exists;
- `完成证据` (`completion_evidence`): the contract's completion condition is
  evidenced;
- `已批准下一步就绪` (`preapproved_next_ready`): the trigger for a
  preapproved supervisor action is evidenced.

Use a compact Chinese report structure such as `事件`, `对象`, `证据`, `判断边界`,
and `建议下一步`. Do not emit an unchanged-status report merely because a timer
expired.

An event never assigns a coordination-line state and never proves final task
completion. The coordinator performs intake, and `personal-risk-verification`
owns any final completion claim.

## Observer And Record Boundaries

Every observer contract is read-only. `prompt_only` is a disclosed behavioral
boundary for the low-risk tier, not proof of an effective sandbox. An observer
may inspect only the assigned job and evidence paths and return an event to the
supervisor. It must not:

- stop, restart, repair, or reconfigure the job;
- mutate job outputs, checkpoints, logs, or artifacts;
- launch the next stage or another worker;
- publish, clean, commit, or change external state; or
- make a go/no-go, line-status, or completion decision.

Do not create a durable monitoring directory by default. If the user requires a
record, the main process may write the compact authoritative control-plane
record to a specific authorized path such as `.codex/monitoring/<job-id>/`.
Keep only compact state and a short report, make that path an exclusive
mutation, and redact secrets. A read-only observer does not write the record.

## Main-Process Intake

The main process waits for agreed events without duplicating observer polling.
On an event it checks provenance, current phase, contract thresholds, and the
observer's evidence before deciding what happens next.

After that decision, the job-owning executor may repair, restart, terminate, or
launch another stage only when that exact action was preapproved. The main
process scopes and authorizes the action; it does not execute substantive job
work. Ask before an unapproved action, scope change, material cost change,
resource change, environment change, or data-risk change.
