# Investigation Techniques

Read this reference only for multi-component systems, deep call chains,
flakiness, hangs, state pollution, or a need for additional defensive layers.
Keep the main failure packet as the authoritative summary.

## Component-Boundary Tracing

Identify where expected state first stops propagating correctly. Record only
the boundaries relevant to the active hypothesis:

| Boundary | Observed input | Observed output | Config or state source | Expected | Evidence |
| --- | --- | --- | --- | --- | --- |
| caller -> callee | redacted summary | redacted summary | source category | contract | path, line, or command |

- Start at the failing boundary and expand one component at a time.
- Record whether required configuration is present and where it came from; do
  not print credential or environment values.
- Prefer existing logs, debug endpoints, and flags. A source or persistent
  configuration edit for instrumentation requires edit authority.
- Treat missing propagation as a boundary finding, not yet the initiating root
  cause. Trace the producer of the missing or invalid state.

## Backward Data And State Tracing

Walk backward through values, state transitions, and callers:

1. Identify the operation that observed the invalid state.
2. Identify the value or state that made the operation fail.
3. Find the producer, caller, or transition that supplied it.
4. Repeat until reaching a violated contract, initiating change, or strongest
   observable external boundary.
5. Verify the chain with a discriminating observation or intervention.

Do not patch a default at the crash site when the producer can be corrected.
When the source is external or inaccessible, stop at the strongest evidenced
boundary and mark the internal cause `likely` or `unknown`.

## Recent-Change Differential

Check only changes plausibly connected to the failure:

- source and test diffs;
- configuration, dependency, lockfile, image, or toolchain changes;
- environment owner, device, data, input, and execution-order differences;
- permission, storage, network, locale, clock, concurrency, and resource state.

Separate temporal correlation from causation. A recent change becomes causal
evidence only when its predicted effect survives a discriminating check.

## Working/Broken Comparison

Choose the nearest trustworthy comparator: the same repository and version,
the same component on a passing path, or an authoritative contract.

Compare:

- inputs and preconditions;
- dependency and configuration sources;
- call order and state transitions;
- environment and resource assumptions;
- outputs, errors, and cleanup behavior.

List material differences before selecting one to test. Do not copy a working
implementation until its assumptions and dependencies are understood.

## Flakes, Hangs, And Condition Waiting

For flakes, record the variables that can change between runs: seed, order,
parallelism, time, clock, cache state, shared files, data shard, device,
resource pressure, and external availability. One pass does not disprove a
flake and one failure does not establish its cause.

When an arbitrary sleep only guesses when a condition becomes true, prefer a
bounded condition wait:

- poll fresh observable state rather than cached state;
- use a finite deadline and a reasonable interval;
- report the last observed state in the timeout error;
- stop promptly when the condition is satisfied;
- preserve explicit time assertions when timing itself is the contract, such
  as debounce or throttle behavior.

A condition wait inside a test is a bounded test technique. It is not an
active-monitoring contract for a long-running job.

## Pollution And Order Dependence

Use the project's runner and isolation model. Prefer a bounded group or binary
search over unbounded one-by-one execution:

1. Establish a clean or known baseline without deleting user work.
2. Identify the polluted state and when it first appears.
3. Run the smallest authorized subset capable of distinguishing groups.
4. Reset only test-owned state between groups through the project's supported
   mechanism.
5. Confirm the candidate polluter alone and in the necessary order.

Do not import a generic polluter script that assumes a package manager, ignores
runner failures, or can launch an unbounded suite. Installation, large suites,
and long or heavy experiments retain their normal authorization boundaries.

## Risk-Based Defense In Depth

Fix the evidenced source first. Add another guard only when it has independent
failure value, such as protecting a separate entry path or preventing a severe
side effect.

- Avoid repeated validation that can drift or produce conflicting errors.
- Give each guard a distinct contract and focused test.
- Add observability only when it helps distinguish future failures; redact
  sensitive data and avoid dumping complete environments or inputs.
- Treat new validation, retry, timeout, or guard behavior as a behavior change
  owned by `personal-test-first-changes`.

## Temporary Instrumentation

- Prefer existing observability first.
- Keep approved probes narrow, time-bounded, and attributable to one
  hypothesis.
- Do not persist source logging or configuration under diagnosis-only authority.
- Place an approved one-off helper or transformed artifact under the owning
  project's temporary-work convention, then preserve or clean it according to
  its audit value.
- Remove or separately authorize temporary instrumentation before completion;
  never leave secrets in code, logs, commands, or artifacts.
