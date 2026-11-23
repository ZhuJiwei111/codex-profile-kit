# Observation Contract Schemas

Pass each object through one `--monitor` option. Unknown kinds and fields are rejected; only one monitor of each kind is allowed.

## NVIDIA process idle

```json
{"kind":"gpu_process_idle","devices":[0,"GPU-uuid"],"mode":"any","utilization_below_percent":5,"duration_seconds":900,"startup_grace_seconds":300}
```

`devices` accepts current NVIDIA indices or UUIDs and is normalized to UUIDs at registration. `mode` defaults to `any`; `sample_interval_seconds` defaults to 10. Samples match NVIDIA process IDs to the target process tree. This requires the driver and procfs PID identities to be comparable. Numeric PID matches alone do not establish that property inside a container; do not claim container attribution verified from capability discovery. Aggregate device utilization is never used as fallback.

Missing target samples or unsupported utilization (`-`) are evidence gaps, not zero utilization. A sustained gap produces `gpu_probe_error` and breaks the continuous-idle timer; it does not stop the job. Capability discovery checks the sampling interface, not a future target PID mapping. A target with no attributable sample (including one that has released its GPU context) cannot be diagnosed as GPU-idle by this monitor; use its actual job output or an already-owned heartbeat for progress. No device-wide fallback or synthetic heartbeat is added.

## Disk free

```json
{"kind":"disk_free","paths":["/absolute/output"],"available_below_gib":20,"available_below_percent":5,"duration_seconds":60}
```

At least one threshold is required; when both are present, either one activates the condition. Paths are normalized and duplicate filesystems are sampled once. `sample_interval_seconds` defaults to 30.

## Heartbeat stale

```json
{"kind":"heartbeat_stale","path":"/absolute/heartbeat","stale_after_seconds":600,"startup_grace_seconds":0}
```

The job must own the heartbeat contract. A missing file ages from registration time. `sample_interval_seconds` defaults to 5. The legacy `--heartbeat-path` plus `--stale-after` pair remains an alias and cannot be combined with this JSON kind.


## Stage snapshot

Local and SSH remote `start` accept `--stage-path PATH` (relative to the target
working directory or absolute). This is a task input, not a health monitor. The
worker supplies `SUPERVISOR_JOB_ID` and resolved `SUPERVISOR_STAGE_PATH` to the
target. The existing pipeline coordinator atomically replaces this JSON file at
meaningful transitions; node workers do not race to publish global stages.

```json
{"job_id":"<SUPERVISOR_JOB_ID>","seq":1,"stage":"CV scoring","facts":"Generation accepted: 4800 images","evidence":"outputs/generation-acceptance.json"}
```

`job_id`, `seq`, and `stage` are required. `seq` is an integer from 0 through
2**53-1, increasing for every new snapshot within the job; a return to an earlier
stage uses a higher sequence. `stage` is nonempty text (up to 160 characters).
Optional `facts` and `evidence` are text (up to 512 characters each); reference
native evidence rather than copying results. Maximum file size is 8 KiB. Write a
temporary sibling and atomically rename it over the destination after closing it.
Use a separate file per concurrently running job; do not inherit another run's ID.

The existing worker samples at most every two seconds while running and once at
exit. It emits the first valid snapshot and later higher sequences as
`stage_changed`, with the snapshot under `stage`. Duplicates do not emit events.
Missing/invalid/foreign or stale snapshots leave the last accepted snapshot intact;
`inspect_job.stage_state.evidence_gap` explains the observation gap, without a
health alert or stopping the target. `stage_state.snapshot` is the last observed
stage, not proof that it is still running. Terminal results remain authoritative.
Wait and acknowledgment use the existing event IDs; list/inspect include stage
state. Stage state is kept in the existing event store, not a separate ledger.

Use this input only on newly launched jobs. It neither starts subsequent stages
nor changes authorization or scientific acceptance. ETA is calculated and reported
by the task owner from current evidence, not supplied by the plugin.
