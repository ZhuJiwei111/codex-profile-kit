# Evidence And ETA

Read this reference only after one local job has been identified. Select the
least invasive evidence that can distinguish its current state. Do not turn a
snapshot into monitoring.

## Evidence Order

Prefer evidence in this order, while applying the job's declared success
contract:

1. An exact scheduler, launcher, or retained process handle with start identity
   and exit status.
2. An explicit success or failure marker tied to this invocation.
3. Required final artifacts validated against their expected count, shape, or
   manifest.
4. Two or more comparable progress observations with timestamps.
5. A known-safe, bounded log milestone when structured evidence is unavailable.

No single signal is universally sufficient. For example, exit code zero may
still require a final manifest, while a complete file count may precede final
flush or validation. State which contract signal is present and which remains
missing.

## Safe Bounded Probes

Use exact identifiers and format only the fields needed for the answer.
The examples below use the current Linux host's tools and syntax. Read
`~/.codex/HOST_LOCAL.md` when host behavior matters, confirm each tool at use
time, and choose an equivalent exact-target probe rather than copying these
commands onto another host.

### Time And Exact Process Identity

```bash
date '+%F %T %Z'
ps -p "$pid" -o pid=,lstart=,etime=,stat=
```

Compare `lstart` with the recorded launch time or retained identity. A live PID
without an identity match is `unknown`, not proof that the original job is
running. A missing PID without an observed exit status is also `unknown`; it
does not prove success or failure.

Do not print full arguments, environment variables, `/proc/<pid>/cmdline`, or
system-wide process matches. Command arguments and environments can contain
tokens, authenticated URLs, dataset names, or private paths.

### Exact `tmux` Session Or Scheduler Job

For a known session, check only that session:

```bash
tmux has-session -t "$session"
tmux list-panes -t "$session" -F '#{pane_pid} #{pane_dead} #{pane_dead_status}'
```

Do not capture pane contents by default; terminal scrollback may contain
secrets or unrelated commands. For a known scheduler job ID, use the scheduler's
single-job query and request only state, start/end time, elapsed time, progress
fields, and exit status. Do not enumerate the queue.

Session presence proves only that the session exists. Session absence does not
prove that a detached child failed, and pane exit does not prove the task's
success contract.

### Known Artifacts

Prefer metadata or aggregate counts over filenames and contents:

```bash
stat --format='%n %s %y' -- "$known_artifact"
wc -l -- "$known_manifest"
find "$known_output_dir" -maxdepth 1 -type f -printf '.' | wc -c
```

Keep the path exact and already in scope. Bound `find` depth and output. Do not
walk the project, home directory, or mounted datasets to infer which job is
active. Use content validation only when the expected artifact contract is
known and the read is proportionate.

### Known-Safe Log Markers

Treat logs as potentially secret-bearing. Prefer counts, timestamps, structured
status records, or a narrowly selected progress pattern whose format is known.
Read the minimum matching lines needed and redact secret-like values before
reporting. Do not use a raw trailing log dump as the default and do not follow a
log.

If the log format is unknown or may contain credentials, skip content and use
file metadata or another signal. Report that omission as an evidence limit.

## State Classification

Classify the dimensions independently.

### Process State

- `running`: the exact retained identity or scheduler job is currently live.
- `exited`: an authoritative launcher, scheduler, or retained handle observed
  its exit.
- `unknown`: visibility is missing, the PID may have been reused, or only an
  uncorrelated presence/absence signal exists.

### Progress State

- `advancing`: two comparable observations show positive forward movement.
- `suspected-stall`: the target is live but no movement occurred across a
  meaningful job-specific interval. This is an observation, not a diagnosis.
- `complete`: the declared progress target is reached; final task success may
  still be unconfirmed.
- `failed`: an authoritative nonzero exit, scheduler failure state, or explicit
  invocation-bound failure marker exists.
- `unknown`: the target, denominator, or comparable observations are missing.

Do not classify one old modification time as a stall, or one unchanged sample
as failure. Variable phases, buffering, checkpoint intervals, and finalization
can make progress appear flat.

### Completion Evidence

- `confirmed`: every success signal required by the known job contract is
  present.
- `not-confirmed`: the job or progress state is known, but at least one required
  success signal is absent.
- `unknown`: the success contract or its evidence is unavailable.

This is job evidence, not a task-readiness verdict. Route final requirement and
verification claims to `personal-risk-verification`.

## ETA Calculation

Use a progress denominator and at least two timestamped observations. With
completed units `n1`, `n2`, observation times `t1`, `t2`, and target `N`:

```text
recent_rate = (n2 - n1) / (t2 - t1)
remaining_time = (N - n2) / recent_rate
```

Use the recent rate when the phase and unit cost are stable. Compare it with the
whole-run average when launch time and initial count are reliable. If the rates
diverge materially, explain the phase change or use the slower credible rate
for a conservative bound.

Report:

- a best estimate rounded to a useful unit rather than false precision;
- a conservative range when rate variance or finalization cost is visible;
- the observation window and unit counts supporting the estimate;
- confidence as `high`, `medium`, or `low`.

Use `high` only for a stable recent rate, clear denominator, and small known
finalization cost. Use `medium` when the denominator is clear but rate or final
overhead varies. Use `low` for a short window, heterogeneous units, or an
inferred denominator.

Report ETA as `unknown` when the denominator is absent, fewer than two useful
observations exist, the rate is zero or negative, phases are not comparable,
the job is queued or suspected stalled, target identity is uncertain, or only
hidden model work remains. Name the one missing measurement that would make a
later estimate meaningful; do not start that later check.

For an observable Codex task, estimate only an explicit bounded remainder such
as one known command, file edit, or verification pass with grounded duration.
Never convert model reasoning effort, token activity, elapsed silence, or a
generic task phase into a time-to-answer estimate.

## Reporting Safety

- Report observations with timestamps and label inferences.
- Redact tokens, passwords, cookies, private URLs, credentials, and secret-like
  values as `<REDACTED>`.
- Do not paste command arguments, raw logs, environments, or private task-store
  records.
- If the smallest safe probe still needs new permission or broader host access,
  return `unknown` and state the exact evidence gap. This skill does not acquire
  broader authority for itself.
