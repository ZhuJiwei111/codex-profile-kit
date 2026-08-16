# Observation Contract Schemas

Pass each object through one `--monitor` option. Unknown kinds and fields are rejected; only one monitor of each kind is allowed.

## NVIDIA process idle

```json
{"kind":"gpu_process_idle","devices":[0,"GPU-uuid"],"mode":"any","utilization_below_percent":5,"duration_seconds":900,"startup_grace_seconds":300}
```

`devices` accepts current NVIDIA indices or UUIDs and is normalized to UUIDs at registration. `mode` defaults to `any`; `sample_interval_seconds` defaults to 10. Samples use only the target process tree. An unrelated process on the same GPU cannot make the monitored job appear active, and aggregate device utilization is never used as fallback.

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
