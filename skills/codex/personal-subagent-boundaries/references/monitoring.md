# Active Monitoring Protocol

Read this reference only after the user explicitly authorizes active monitoring
for the current stage. It is not a trigger to create a watcher.

## Entry Gate

The durable long-running-work instructions own launch authorization, detached
execution, the bounded startup guard, and the handoff required when monitoring
is not authorized. This protocol consumes the startup result; it does not
extend or repeat the startup guard.

Before spawning a monitoring observer, confirm:

- the current stage has explicit active-monitoring authorization;
- the job, phase, process or session, evidence paths, and completion condition
  are known;
- checks can remain read-only with respect to the job and its outputs;
- the `monitor` custom profile can be selected and its effective model,
  reasoning effort, and read-only sandbox are verified; and
- the supervisor will remain responsible for judgment and any later action.

If the configured low-cost, read-only profile cannot be selected and verified,
default to no watcher. Use another profile only when the contract explicitly
names a verified fallback and its cost and reasoning implications are accepted.

## Monitoring Contract

Define this contract before delegation:

```yaml
monitoring:
  job_id:
  phase:
  permission_scope:
  cwd:
  command:
  session_or_pid:
  log_path:
  output_path:
  expected_artifacts: []
  startup_guard_result:
  execution_profile:
    requested_role: monitor
    requested_model:
    requested_reasoning_effort: low
    selection_mechanism: custom_agent | explicit_override | runtime_choice
    enforcement: verified
    fallback: no_monitor
  health_signals: []
  job_specific_thresholds: []
  fallback_thresholds: []
  cadence:
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

`preapproved_next_actions` lists actions the supervisor may later execute. It
does not authorize the monitoring observer to execute them.

## Model And Reasoning Boundary

The configured `monitor` role is for deterministic collection and threshold
comparison at low reasoning effort. The parent agent's current profile is not
the monitor's quality or cost baseline.

When a monitoring contract requires ambiguous ETA inference, correlation of
multiple weak signals, or causal analysis that cannot be expressed as bounded
checks, choose a suitable balanced profile before launch or keep that analysis
with the supervisor. Do not silently raise a running observer's model or
reasoning effort. If the work becomes diagnosis, emit `action_needed` and hand
off to a separately scoped diagnostic workflow.

## Cadence

Derive cadence from the expected runtime, early failure window, first visible
progress point, log or artifact update frequency, and next meaningful event.

- Prefer event-driven waits and sparse checks over polling loops.
- Check earlier only when startup risk remains material after the startup
  guard.
- Back off after stable evidence.
- Do not read logs, artifacts, process state, and GPU state merely because a
  wait timeout elapsed; perform the next contract-defined check.
- A sparse cadence never suppresses an anomaly found during an authorized
  check.

Do not encode one global numerical interval for all jobs. Record any numerical
cadence in the job contract where its rationale can be reviewed.

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

Use non-authoritative event names:

- `milestone`: a contract-defined progress boundary is evidenced;
- `action_needed`: ambiguity or anomaly requires supervisor or user judgment;
- `failure_evidence`: direct process, log, or contract-defined failure evidence
  exists;
- `completion_evidence`: the contract's completion condition is evidenced;
- `preapproved_next_ready`: the trigger for a preapproved supervisor action is
  evidenced.

An event never assigns a coordination-line state and never proves final task
completion. The coordinator performs intake, and `personal-risk-verification`
owns any final completion claim.

## Observer And Record Boundaries

The standard `monitor` profile is read-only. It may inspect only the assigned
job and evidence paths and return an event to the supervisor. It must not:

- stop, restart, repair, or reconfigure the job;
- mutate job outputs, checkpoints, logs, or artifacts;
- launch the next stage or another worker;
- publish, clean, commit, or change external state; or
- make a go/no-go, line-status, or completion decision.

Do not create a durable monitoring directory by default. If the user requires a
record, assign a separate authorized writer—normally the supervisor—to a
specific path such as `.codex/monitoring/<job-id>/`. Keep only compact state and
a short report, make that path an exclusive mutation, and redact secrets. A
read-only observer does not write the record itself.

## Supervisor Intake

The supervisor waits for agreed events without duplicating observer polling.
On an event it checks provenance, current phase, contract thresholds, and the
observer's evidence before deciding what happens next.

The supervisor may repair, restart, terminate, or launch another stage only
when that exact action was preapproved. Ask before an unapproved action, scope
change, material cost change, resource change, environment change, or data-risk
change.
