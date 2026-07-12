---
name: personal-risk-verification
description: Use as the single final gate after task-owned local changes and before claiming they are complete, fixed, passing, or ready for handoff; not for intermediate tests, diagnosis, or Git/PR actions.
---

# Personal Risk Verification

Act as the single final local completion gate. Decide whether the current
task-owned state supports the intended completion claims after the last
relevant change. Consume earlier workflow evidence without confusing an
intermediate pass, a worker report, or a clean-looking diff with completion.

Do not create missing implementation, investigate an unexpected failure, or
start the next workflow from inside this gate. Report the actual state and hand
the gap to its owner.

## Lock The Completion Basis

For a non-trivial task, keep this compact record in the conversation:

```yaml
completion_basis:
  requested_outcome:
  acceptance_criteria:
  approved_scope:
  applicable_instructions:
completion_claims:
  - requirement:
    claim:
    evidence_needed:
final_state:
  task_owned_changes:
  unrelated_changes:
  last_relevant_changes:
evidence:
  - check:
    target_revision:
    cwd:
    environment:
    expected:
    observed:
    exit_status:
    fresh_for:
not_run:
  - check:
    reason:
    consequence:
remaining_risk:
```

Keep the record implicit for one small, obvious change. Do not create a state
file merely to perform final verification.

## Invalidate Evidence By Relevance

Treat evidence as fresh only when it applies to the state being claimed:

- A later overlapping code, configuration, schema, generator, or dependency
  change invalidates the affected behavior, type, build, or artifact evidence.
- A later documentation change invalidates the affected readback, literal,
  link, example, and final-diff evidence. It does not automatically invalidate
  runtime evidence when the runtime contract and inputs are unchanged.
- Inspect the final diff or artifact after all task-owned changes. Earlier diff
  inspection cannot prove the later state.
- Bind evidence to the current revision, exact files, generated inputs, or
  artifact identity when those facts affect applicability.
- Do not treat an agent's success summary as evidence by itself. Inspect the
  relevant diff and raw result provenance; rerun a critical check when its
  revision, command, coverage, or outcome is uncertain.
- Keep local, remote, and external states separate. A local pass does not prove
  remote CI, PR, deployment, publication, reviewer, or service state.

Freshness is dependency-based, not message-based. Reuse earlier task evidence
when its target has not changed and its coverage still proves the claim; do not
rerun unrelated expensive checks merely for ceremony.

## Map Claims To Direct Evidence

Use the narrowest evidence that directly supports each claim, then broaden only
for the affected blast radius.

| Claim | Direct evidence | Not sufficient by itself |
| --- | --- | --- |
| A bug or behavior is fixed | Current focused reproduction or regression boundary, plus coupled checks when warranted | Code changed or a different test passed |
| Tests pass | Exact current test command, collected scope, failure count, and successful exit | An older run, one subset, or “should pass” |
| Build or package succeeds | The actual build or packaging command and artifact/result | Lint, typecheck, or import success |
| API, schema, or types are valid | Contract, schema, type, parser, import, or consumer check for the changed surface | Unrelated unit tests |
| CLI, script, or config works | Parser, `--help`, syntax, dry-run, or bounded smoke evidence for the changed contract | Documentation text alone |
| Existing docs are current | Post-edit docs evidence from `personal-docs-sync-light` and final readback/diff | Runtime tests alone |
| An artifact is ready | Inspection or validator against the artifact produced from current inputs | Generator invocation without output checks |
| Requirements are met | Requirement-by-requirement review against current behavior and artifacts | Tests passing without scope review |
| Delegated work is complete | Worker evidence plus coordinator inspection of provenance, diff, and required checks | The worker's recommended outcome |

Consume focused RED/GREEN, preserving-baseline, review, debugging, and docs
evidence from their owning workflows. This gate checks freshness, coverage, and
the final combined state; it does not recreate those workflows.

When no executable harness exists, use the strongest proportionate static,
parser, schema, readback, diff, or manual artifact evidence and state the
remaining gap. Lack of a full suite is not automatically failure, but lack of
evidence required for a material claim is.

## Run And Read The Evidence

For each check that must be run or refreshed:

1. Record the exact command or inspection, `cwd`, environment owner, target
   revision or artifact, expected signal, and material side effects.
2. Run it after the last relevant change.
3. Inspect the meaningful output and the exit status. Confirm the observed
   result actually matches the claimed property.
4. For pipelines or wrappers, preserve or inspect each relevant stage's failure
   status; do not let a successful final formatter hide an earlier failure.
5. Detect false passes such as zero tests collected, relevant skipped checks,
   swallowed failures, truncated decisive output, stale cached artifacts, or
   success with warnings that contradict the claim.
6. Keep large output bounded with structured summaries or targeted excerpts,
   while retaining enough raw evidence to support the result.

If a required check fails, report that result and stop the completion claim. A
verification-only failure does not authorize diagnosis or another fix.

## Review Requirements And Final State

After the last task-owned mutation:

1. Re-read the requested outcome, acceptance criteria, approved scope, and
   applicable instructions.
2. Inspect the final task-owned diff, intended untracked resources, generated
   artifacts, and user-visible outputs.
3. Separate unrelated user or prior-stage changes from the completion claim;
   preserve them and do not use them to make the task look clean or complete.
4. Confirm each material requirement has current evidence. Classify deliberate
   exclusions, historical files, unsupported environments, and external state
   without silently treating them as covered.
5. List checks that were not run, why, and what uncertainty each omission
   leaves. Distinguish an unnecessary broader check from missing required
   evidence.

## Issue One Verdict

Use one binary completion verdict:

```yaml
completion_verdict: supported | not_supported
verification_blockers:
not_run:
remaining_risk:
next_owner:
required_authority:
```

- `supported`: every material in-scope completion claim has fresh,
  proportionate evidence. Report non-required checks not run and bounded
  residual risk without implying they were covered.
- `not_supported`: a material requirement failed, remains unknown, lacks
  required evidence, relies on stale or mismatched evidence, or needs a scope or
  authority decision. Do not call the task complete.

Do not add a vague intermediate pass state. If only part of the work is
supported, name that part and the remaining gap under `not_supported`.

Report what changed, requirement coverage, exact checks and outcomes, checks not
run, remaining risk, and the verdict. Never imply that an external action or
state transition occurred when only local evidence exists.

## Respect Authorization And Resources

Use safe, bounded local verification that belongs to the authorized
implementation workflow. Do not install dependencies, create a large
environment, download substantial assets, use heavy GPU resources, start a
long-running check, rerun remote CI, mutate external state, or perform a
destructive action merely to obtain a passing verdict.

If required evidence needs new authority, report `not_supported`, the exact
command or action, resource and time scope, expected success signal, and the
authorization needed. Do not lower the completion standard because time is
short or a worker is waiting.

## Collaboration And Boundaries

- `personal-test-first-changes` owns RED/GREEN, preserving baselines, and
  implementation-phase alternatives.
- `personal-review-response` owns feedback disposition, implementation
  authority, and external review state.
- `personal-evidence-debugging` owns unexpected failures after the gate reports
  them; verification does not silently become diagnosis.
- `personal-docs-sync-light` owns factual documentation synchronization and
  returns post-edit evidence to this final gate.
- `personal-repo-intake` owns genuinely unclear repository root, instructions,
  worktree, harness, or artifact ownership facts.
- `personal-subagent-boundaries` owns worker scope and reporting contracts.
- `personal-multiline-coordination` owns authoritative coordination-line
  intake, per-line decisions, and integration provenance when multiline or
  worktree coordination is active. This gate consumes that evidence; it does
  not set or override coordination-line state.
- This gate alone owns the final task-level `completion_verdict` after
  reviewing the combined current state. That verdict is not a coordination-line
  status and does not retroactively change worker recommendations or
  coordinator decisions.
- `personal-project-output-explainer` may explain a completed verdict to a
  broader audience without changing it.
- `personal-branch-finish` consumes a `supported` verdict for Git readiness,
  commit or PR decisions, and handoff. This skill does not stage, commit, push,
  publish, or create a PR.

## Source Provenance

See [source notes](references/source-notes.md) for the pinned Superpowers
evidence, license, local history, adopted principles, rejected assumptions, and
Codex-specific deviations.
