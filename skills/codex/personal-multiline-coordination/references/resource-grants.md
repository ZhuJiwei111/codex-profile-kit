# Resource And Monitoring Grants

## Separate Actions

Grant these independently per line or stage:

- ordinary network access;
- high-traffic or large downloads;
- package installation or environment creation;
- heavy CPU or memory use;
- GPU device and intensity;
- long-job launch;
- active monitoring;
- repair, stop, or restart contingencies;
- next-stage launch.

Approval for one does not imply another. A worker may inherit a grant only when
the launch manifest names its line, scope, limits, and stage.

## Resource Claims

Represent schedulable claims as:

```json
{"id": "gpu:0", "mode": "exclusive"}
```

Use `exclusive` when concurrent use is unsafe or materially changes cost or
performance. Use `shared_read` only for immutable resources such as a dataset.
Two active claims conflict when they share an id and either is exclusive.

Resource availability is dynamic. Recheck storage, device availability,
process/container limits, network reachability, and environment ownership when
they affect launch.

## Grant Record

For a non-ordinary action, record:

```yaml
line_id: <line>
stage: <stage>
action: <download|gpu|long_job|active_monitoring|repair|restart|next_stage>
scope: <command-data-device-or-session>
limits: <traffic-time-device-storage-or-cost>
success_signal: <observable-signal>
failure_signal: <observable-signal>
contingencies: [<preauthorized-actions-or-empty>]
expires_at: <stage-boundary>
```

Do not copy credentials or authenticated URLs into the grant.

`contingencies` describe actions that the supervisor or coordinator may
execute after monitor evidence is reported and intake is complete. They never
grant a monitoring observer permission to execute those actions.

## Long Jobs

Before launch, map planned to actual command, environment, `cwd`, device,
session/PID, logs, outputs, and success criteria. Follow the durable long-job
rules for detached execution and the bounded startup guard.

The coordinator schedules the line but does not become a polling loop. If
active monitoring is not granted, return a reproducible handoff and one status
command.

Handle an ordinary one-shot status or ETA request through a bounded read-only
inspection. It is neither active monitoring nor authority to mutate the job.

## Active Monitoring

When explicitly granted:

- define the monitoring contract before launch;
- prefer a managed monitoring subagent over a new top-level implementation
  worker unless user-visible durable monitoring is specifically required;
- keep it read-only;
- use sparse, event-driven checks and bounded waits;
- report only material transitions or requested status;
- let the coordinator make the line decision.

A monitor may not stop, repair, restart, mutate outputs, launch a next stage,
change resource scope, or make a line decision. This remains true even when an
exact contingency, trigger, and limit were preauthorized. The monitor reports
the trigger evidence; after intake, the supervisor or coordinator decides and
executes only the separately authorized action.

If model or reasoning controls are exposed, a mechanical monitor normally uses
the least costly setting that can reliably classify its signals. Do not claim a
setting change when the tool surface does not expose it.

## Scheduling

Launch a ready line only when:

- all required dependency decisions permit it;
- its write set and output paths do not conflict with active lines;
- its resource claims are compatible;
- the required grant is current for that stage;
- the actual resource is available.

Do not use a fixed concurrency target as a substitute for these checks.
