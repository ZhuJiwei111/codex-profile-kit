---
name: personal-evidence-debugging
description: Use to investigate unexpected local failures, flakes, hangs, or failed fix attempts before another change; not for expected RED or status-only checks.
---

# Personal Evidence Debugging

Trace an unexpected failure to the strongest supported causal explanation
before another change. Do not stack patches on symptoms.

## Lock Scope And Authority

Set `diagnosis_scope` before acting:

- `diagnosis_only`: use read-only inspection, existing debug options, changes
  to queries or inputs, and isolated ephemeral probes that do not modify task
  code or durable configuration. Stop after explaining the cause and evidence.
- `fix_authorized`: investigate first, then hand a confirmed or bounded cause
  to the implementation workflow. Authorization to fix does not waive the
  evidence gate.

A verification-only failure does not automatically authorize diagnosis. Report
it and stop unless diagnosis is already in scope. A reason-matched expected RED
remains with `personal-test-first-changes`; a wrong-reason RED, flake, hang, or
unexpected GREEN belongs here. For an unnamed ordinary status or ETA request,
leave specialist workflows and use one bounded ordinary read-only status check.
Use `$personal-long-job-status` only after explicit skill invocation.

## Keep A Failure Packet

Maintain this compact record in the conversation; do not create a state file:

```yaml
diagnosis_scope: diagnosis_only | fix_authorized
expected:
observed:
exact_command:
cwd:
environment_owner:
exit_status:
first_failure:
reproduction: deterministic | flaky | hanging | not_reproduced
frequency:
first_seen:
recent_relevant_changes:
boundary_evidence:
working_comparator:
active_hypothesis:
prediction:
falsifier:
check_result:
root_cause_status: confirmed | likely | unknown
fix_attempts:
next_owner:
```

Record the earliest causally useful failure, not merely the last log line. Keep
commands, exit status, relevant artifact paths, and compact error evidence.
Redact secret values, authenticated URLs, cookies, tokens, private inputs, and
credential-bearing environment data.

## Investigation Loop

### 1. Lock The Failure Contract

- State expected versus observed behavior and the exact boundary where they
  diverge.
- Distinguish an expected nonzero result, an expected test RED, and an
  unexpected failure.
- Confirm the task-owned `cwd`, environment owner, and relevant input. Use
  `personal-repo-intake` only when those repository facts are genuinely
  unclear.
- Separate related evidence from unrelated baseline failures. Never hide a
  failed command or expand scope to repair unrelated failures.

### 2. Reproduce And Classify

- Reproduce with the narrowest proportionate check when practical.
- Classify the result as deterministic, flaky, hanging, environmental,
  resource-related, data-related, integration-related, or not reproduced.
- If the full reproduction is expensive, use a cheaper proxy and state exactly
  what causal link it can and cannot establish.
- Stable repetition establishes reproducibility; it is not a failed fix.

### 3. Inspect Changes, Boundaries, And Comparators

- Check task-relevant recent code, configuration, dependency, environment,
  device, input, and data changes.
- At component boundaries, compare observed input, output, state, and
  configuration propagation against the contract.
- Find the closest working path or implementation in the same repository and
  version. Enumerate material differences instead of copying it blindly.
- For multi-component systems, deep call chains, flakes, hangs, or state
  pollution, read
  [investigation techniques](references/investigation-techniques.md).

### 4. Test One Hypothesis

State one specific hypothesis, its mechanism, a prediction, and a falsifier:

```text
X is the cause because Y.
If X is true, check Z should produce P.
Result Q would falsify X.
```

Use the smallest discriminating experiment and change one diagnostic variable
at a time. Correct an obvious probe error without changing product behavior.
If two diagnostic cycles return the same evidence without new discriminating
information, change layer or tactic; do not count those cycles as fixes.

### 5. Trace To The Cause

Trace backward from the symptom:

```text
observed symptom
  <- failing boundary
  <- first invalid state
  <- producer or caller
  <- violated contract or initiating change
```

Distinguish the symptom, immediate cause, contributing factors, and initiating
root cause. Assign:

- `confirmed`: a specific mechanism explains the symptom and a discriminating
  intervention or counterfactual changes the evidence as predicted;
- `likely`: it is the strongest supported explanation, but an external,
  hardware, timing, or otherwise unobservable boundary prevents confirmation;
- `unknown`: evidence shows only correlation, a symptom location, or competing
  explanations.

Do not claim an inaccessible third-party internal cause as confirmed. A bounded
fallback, error handler, or observability improvement may still be proposed if
its evidence boundary and residual uncertainty are explicit.

## Fix Handoff And Verification

- For `diagnosis_only`, report the mechanism, root-cause status, evidence,
  unknowns, and smallest useful next action, then stop.
- For `fix_authorized`, hand the reproduction, causal evidence, intended edit
  boundary, and success signal to `personal-test-first-changes`. That workflow
  owns regression RED, implementation, and focused GREEN.
- If the fix does not remove the target failure, return here with the result as
  new evidence. Do not stack another speculative patch.
- After a fix mechanism passes, return to `personal-risk-verification` for the
  only final completion gate and fresh post-change evidence.

## Three-Failed-Fix Architecture Gate

Count one `failed_fix_attempt` only when all are true:

- an authorized product change was actually applied;
- it represented an explicit, attributable causal or fix hypothesis;
- it was isolated from other fixes;
- a valid post-change check actually ran; and
- the target failure remained or a new related symptom appeared.

Do not count command reruns, reproduction failures, setup or fixture errors,
read-only inspection, diagnostic instrumentation, falsified hypotheses without
a product change, bundled unattributable patches, or unlaunched heavy tests.

After three independent failed fixes for the same target problem:

1. Do not attempt fix four.
2. Summarize each hypothesis, change, prediction, check, result, and new
   symptom.
3. Reassess the reproduction, ownership, component boundary, interface
   contract, shared state, coupling, and possibility of multiple causes.
4. Discuss the data model, interface boundary, scope, acceptance criteria, or
   architecture with the user.
5. Wait for a new direction and authorization before another implementation.

This gate means the current fix model has failed. It does not by itself prove
that the whole architecture is wrong.

## Long-Running And Resource Boundaries

- A failed long job does not authorize a restart.
- When the request is only ordinary status or ETA, leave this workflow and use
  one bounded ordinary read-only status check. Within an actual diagnosis
  request, inspect at most one bounded read-only log, artifact, or status
  surface. Do not tail, poll, create a watcher, kill, repair, or restart it
  without the corresponding authorization.
- Treat a reproduction or rerun expected to exceed 10 minutes as a new
  long-running launch. State its command, environment, resource scope, outputs,
  expected duration, and success signal before requesting approval.
- Do not install a missing dependency, create a large environment, download
  assets, or use heavy GPU resources merely to complete the investigation.
  Obtain the required environment and resource authorization first.
- Use an explicit device scope for an approved GPU reproduction. A bounded
  startup guard is not active monitoring.
- A bounded condition wait inside a test or diagnostic probe is not permission
  for continuous job monitoring.

## Collaboration And Durable Guidance

- `personal-context-optimization` may reduce repeated log reads or preserve
  precise anchors; it does not own the causal investigation.
- `personal-subagent-boundaries` may isolate independent read-only evidence
  domains. Give workers the same failure packet and allow only one fix owner;
  do not vote among competing root causes—design a discriminating check.
- `personal-temporary-work` owns the lifecycle of an approved one-off
  reproducer, parser, or transformed artifact; this skill still owns the
  hypothesis and evidence.
- `personal-branch-finish` begins only after the failure is resolved and final
  verification passes.

Do not update `AGENTS.md` merely because a failure repeated. Route durable
guidance to the narrowest owner only when the root cause is confirmed, the rule
is genuinely reusable, and that documentation or instruction change is itself
authorized.

See [source notes](references/source-notes.md) for upstream provenance,
adopted techniques, rejected assumptions, and local deviations.
