# Advanced Investigation Techniques

Use these techniques only when the fast path cannot resolve a flake, hang, deep
call chain, state leak, or multi-component failure.

## Trace Boundaries Backward

Start at the first observed invalid state. Inspect the relevant input, output,
configuration source, and expected contract at that boundary, then trace the
producer or caller backward until reaching a violated contract or the strongest
observable external boundary.

Missing propagation identifies a failing boundary, not automatically the root
cause. Verify the chain with a discriminating observation or intervention.

## Compare Working And Broken Paths

Choose the nearest trustworthy comparator in the same repository and version.
Compare inputs, preconditions, configuration, dependency sources, call order,
state transitions, environment assumptions, outputs, errors, and cleanup.

List material differences before selecting one to test. Temporal proximity or a
recent diff becomes causal evidence only when its predicted effect survives the
check.

## Investigate Flakes And Hangs

Track variables that may change between runs: seed, order, parallelism, clock,
cache, shared files, data shard, device, resource pressure, and external
availability. One pass does not disprove a flake, and one failure does not
establish its cause.

When elapsed time is only a proxy for readiness, prefer a bounded wait on fresh
observable state with a finite deadline and a useful timeout message. Preserve
explicit time assertions when timing itself is the contract.

## Find State Pollution

Use the project's supported isolation mechanism. Compare bounded groups or use a
binary split rather than launching an unbounded one-by-one suite. Reset only
test-owned state, and confirm the candidate polluter alone and in the required
order.

## Instrument Temporarily

Prefer existing logs and debug flags. Keep any authorized probe narrow,
time-bounded, and tied to one hypothesis. Do not persist source logging or
configuration under diagnosis-only authority, and never include secrets in
commands, logs, or artifacts.
