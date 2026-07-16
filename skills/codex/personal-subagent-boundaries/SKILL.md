---
name: personal-subagent-boundaries
description: Use when the user asks for subagents or bounded work can be delegated for independent exploration, review, validation, or exclusive-file edits; not for auto-monitoring.
---

# Personal Subagent Boundaries

Delegate only when isolation improves speed, quality, or independence. This
skill owns a bounded delegation decision, the worker contract, exclusive
mutation boundaries, worker reporting, and delegator intake.

It does not own persistent line or worktree state, authoritative coordination
status, final completion, Git finish actions, or temporary artifact lifecycle.

## Trigger And Independence Gate

Use this skill when the user asks for subagents or when a bounded explorer,
reviewer, validator, or editing worker could materially help. Keep work local
when it is a simple critical-path action, depends on an unresolved design
decision, needs unbounded conversation context, or costs more to coordinate
than it returns.

Parallel delegation is appropriate only when:

- each objective can use frozen or otherwise stable inputs;
- workers do not need one another's intermediate decisions;
- every mutable resource and indirect side effect can be assigned exclusively;
- a worker's report remains useful at its stop condition; and
- coordination overhead is lower than the expected speed, isolation, or review
  benefit.

Use one writer with readers bound to a fixed revision when work shares a code
or artifact surface. Do not use worker votes as a correctness decision. Ask
workers for discriminating evidence and let the coordinator decide after
intake. If overlap or a hidden dependency appears, stop the affected worker and
reassign or serialize the work from a visible state.

Use `personal-multiline-coordination` for persistent lines, multiple worktrees,
or long-lived/stateful worker sets that need dependency and resource gates,
cross-line integration provenance, recovery decisions, or authoritative line
status. One-shot independent workers still receive the light intake defined
here.

## Choose An Execution Profile

Choose a profile from the role, task complexity, risk, and verifiability. Do
not downgrade work merely because it is delegated, and do not treat the parent
agent's current model or reasoning effort as the quality baseline.

Resolve semantic requirements before literal model settings:

- `routine`: deterministic collection, lookup, or threshold comparison;
- `balanced`: bounded synthesis, ordinary implementation, or multi-signal
  interpretation;
- `deep`: complex logic, independent consequential review, or causal analysis.

Use a stable custom profile only when the role has predictable reasoning and
sandbox needs:

- `monitor`: explicitly authorized, deterministic, read-only monitoring;
- `reviewer`: independent, read-only, consequential review.

Keep explorer, worker, validator, and diagnostic profiles task-dependent.
Inherit a parent profile only after confirming it satisfies the task; otherwise
use a supported custom profile, explicit override, or runtime choice. If the
current spawn surface cannot select or verify the requested profile, record it
as unverified or unavailable rather than claiming it took effect.

Treat a custom file's `sandbox_mode` as requested configuration, not proof of
the effective sandbox: current-session runtime overrides can be reapplied when
Codex spawns a child. If read-only enforcement is safety-critical, verify the
effective child sandbox or keep the task local.

## Keep Four Role Contracts Distinct

- **Main process or coordinator:** owns scope, authority, task packets,
  scheduling, intake, synthesis, authoritative coordination state, and the only
  task-level verdict. It keeps context bounded and does not absorb substantive
  implementation, test, or recurring log work merely because delegation is
  inconvenient.
- **Executor:** performs the bounded substantive read, edit, command, test,
  validation, diagnostic, integration, or one-shot observation work. It returns
  raw evidence and may report a non-authoritative `recommended_outcome` when
  that helps intake.
- **Reviewer:** independently examines a fixed revision or artifact and reports
  claims, source anchors, semantic scenario evidence, coverage gaps, and
  uncertainty. It never reports acceptance, rejection, a line state, a
  `recommended_outcome`, or a task verdict.
- **Monitor:** is the sole recurring read-only observer for one exact authorized
  job and phase. It reports evidence events and uncertainty only; it never
  decides, mutates, repairs, restarts, or advances work.

The main process may write only the compact authoritative coordination state
owned by the active workflow, such as an intake, verdict, or explicitly
authorized monitoring record. Product files, tests, generated outputs, command
logs, and integration mutations belong to an executor with an exclusive
surface.

## Build The Minimal Contract

Define this information before spawning:

```yaml
delegation:
  objective:
  actor_role: executor | reviewer | monitor
  mode: explore | implement | validate | diagnose | observe_once | review | monitor
  canonical_cwd:
  branch_or_worktree:
  target_revision:
  context_anchors: []
  read_only_inputs: []
  exclusive_mutations: []
  allowed_actions: []
  forbidden_actions: []
  execution_profile:
    role:
    capability_class: efficient | capable | strongest_available
    reasoning_class: routine | balanced | deep
    requested_model:
    requested_reasoning_effort:
    source: custom_profile | explicit_override | runtime_choice | inherit_after_check
    enforcement: verified | configured_unverified | prompt_only | unavailable
    fallback:
    effort_ceiling:
    escalation_target:
  verification_expectation:
  stop_condition:
  report_contract:
```

Pass only the paths, symbols, revisions, accepted decisions, constraints, and
raw artifacts needed for the objective. Use the smallest sufficient
`fork_turns`; prefer `none` for a self-contained independent review. Do not
forward the full conversation when a self-contained task packet is sufficient,
disclose secrets, or tell an independent reviewer the conclusion it is expected
to reach. Use full inheritance only when the objective genuinely cannot be made
self-contained and sensitive context has been screened first.

## Protect The Mutation Surface

`exclusive_mutations` covers more than manually edited files. Include source,
tests, generated files, lockfiles, snapshots, caches, reports, plans, sync
inputs, databases, ports, output directories, external mutable resources, and
formatter or codegen side effects.

- Never run concurrent writers against overlapping mutation surfaces.
- Bind readers and validators to a fixed revision or stable artifact; do not
  treat a changing live tree as stable evidence.
- A worker must not change worktree, branch, scope, permissions, or ownership
  without a new coordinator decision.
- Do not delegate stage, commit, push, publication, next-stage launch, or
  external mutation unless that exact action is separately authorized and
  assigned.
- If a command writes outside the assigned surface, stop and report the actual
  side effect before continuing.

## Stop And Report

At the stop condition, or when new context, scope, authority, or ownership is
needed, hand off and wait. A worker must not invent or approve the next stage.

Executors use this report; `recommended_outcome` is optional and never becomes
a coordinator decision:

```yaml
executor_report:
  execution_status: scope_finished | boundary_reached | needs_input | cannot_continue
  result:
  changed_paths: []
  produced_artifacts: []
  evidence:
    - command_or_inspection:
      cwd:
      target_revision:
      observed:
      exit_status:
  verification_run: []
  verification_not_run: []
  risks_and_uncertainties: []
  recommended_outcome: accept | reject | needs-more-evidence | omitted
  stop_reason:
  next_safe_action:
```

Reviewers use an evidence-only report:

```yaml
reviewer_report:
  target_revision:
  claims_examined: []
  evidence: []
  semantic_scenarios: []
  coverage_gaps: []
  risks_and_uncertainties: []
  stop_reason:
```

Execution status describes what an executor did, not whether the coordination
line passed. A reviewer report and a monitor event contain no disposition or
recommendation. Only the main process or coordinator may assign authoritative
states such as `pass`, `no-go`, `needs-more-evidence`, or `blocked` after
intake.

## Intake And Reuse

For a one-shot report, the main process or coordinator:

1. confirms the worker, objective, actual `cwd`, revision, and execution mode;
2. checks changed paths and indirect side effects against the assigned surface;
3. reads the relevant diff, artifact, and provenance-bearing evidence;
4. checks commands, exit status, omissions, risks, and evidence freshness;
5. decides `accept`, `reject`, or `needs-more-evidence`; any follow-up or
   rework is a separately stated next action with a redefined scope; and
6. hands any final completion claim about task-owned local changes to
   `personal-risk-verification`; read-only exploration and review stop with
   their evidence report.

```yaml
delegator_intake:
  decision: accept | reject | needs-more-evidence
  evidence_disposition:
  next_action:
```

`next_action` carries any separately scoped follow-up or rework; it is not a
fourth decision value.

Reuse a specific report instead of blindly repeating its exploration. Spot
check when provenance or paths are missing, reports conflict, integration or
safety is involved, credentials may be exposed, evidence may be stale, final
verification needs direct support, or the user asks.

## Active Monitoring

Do not create a watcher by default. For an ordinary status or ETA request, the
main process names the exact job and one evidence surface, and a read-only
executor performs one `observe_once` pass. It reports observed progress,
timestamp or artifact identity, and uncertainty, then stops. It must not wait
again, poll, tail, diagnose, repair, restart, or infer an ETA unsupported by
evidence. This is not active monitoring.

Active monitoring requires explicit authorization in the current Codex thread
and an enforceable per-job monitoring contract. Unless the user narrows or
revokes it, that authorization remains valid for later long-running jobs in the
same thread and on the same host. It authorizes observation only: every new job
or phase still needs a fresh contract, and launch, repair, restart, and stage
progression retain their own authority gates.

The portable custom file requests `monitor`, `gpt-5.6-luna`, high reasoning,
and a read-only sandbox; that is `configured_unverified`, not runtime proof. A
strict monitor is available only when the active spawn surface verifies the
effective role, model, reasoning effort, and sandbox. `prompt_only` or
`configured_unverified` enforcement means strict monitoring is unavailable.
Do not replace it with recurring checks in the main process. Read [the
monitoring protocol](references/monitoring.md) before spawning. User-visible
monitoring reports use Chinese event names; monitoring events remain evidence,
never task completion or a go/no-go decision.

## Collaboration Boundaries

- `personal-multiline-coordination` owns stateful line and worktree
  coordination, recovery, and authoritative coordinator-state workflows.
- `personal-temporary-work` owns helper and temporary artifact lifecycle.
- Domain skills such as brainstorming, review response, test-first changes,
  debugging, and documentation own the substantive work delegated through this
  boundary.
- `personal-risk-verification` is the only final completion gate after
  task-owned local changes.
- `personal-branch-finish` owns later Git readiness and handoff decisions.

## Sources

See [source notes](references/source-notes.md) for pinned Superpowers evidence,
current official Codex custom-agent documentation, local history, adopted and
rejected patterns, and local deviations.
