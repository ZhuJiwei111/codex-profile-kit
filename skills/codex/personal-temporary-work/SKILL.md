---
name: personal-temporary-work
description: Use when one-off migration, conversion, or artifact work might otherwise add permanent code; split the minimal durable change from a temporary helper. Skip simple checks and normal durable features.
---

# Personal Temporary Work

Protect maintained code from one-off transition logic. Separate what future
normal operation must keep from what is needed only to migrate, convert,
repair, inspect, or post-process existing state.

## Split Steady-State And Transition Work

Classify the request before adding a branch, flag, module, parameter, or public
API to maintained code:

- **Steady-state behavior:** future normal users and workflows need it. Make the
  smallest coherent durable change and use its owning implementation workflow.
- **Transition work:** a bounded existing dataset, artifact set, or local state
  needs one-time treatment. Prefer a temporary helper outside maintained code.
- **Hybrid:** future behavior changes and historical state must be migrated.
  Make the minimal durable change for the future and use a temporary helper for
  the existing state.
- **Durable migration surface:** promote migration logic only when positive
  evidence shows repeated operators, environments, releases, versions, formal
  rollback, or ongoing support need it.

Do not run this workflow for a simple command that creates no helper or
artifact. Do not use a temporary helper to avoid implementing a normal durable
feature. When the boundary is not obvious, read
[durable versus temporary](references/durable-vs-temporary.md) before editing.

Default to the temporary helper in an explicitly one-off case with no ongoing
support evidence. Require a positive reason to make transition logic permanent,
not merely the fact that it can be added to the existing script.

## Lock Ownership And The Data Contract

Before creating or modifying files, identify:

- the owning project and worktree, applicable instructions, and task-owned
  mutation surface;
- canonical inputs, whether they must remain immutable, and their provenance;
- the formal deliverable, temporary helper, evidence, staging, and cleanup
  candidates as separate roles;
- ordering, format, overwrite behavior, failure recovery, and the exact
  invariants that prove the requested result;
- the environment, expected scale, resource needs, and retention decision.

Ask one decision-changing question when a missing fact would change output
semantics, ownership, destructive behavior, or placement. Do not invent data
requirements such as ordering, empty-record rules, normalization, or backward
compatibility merely to make a helper look robust.

Compare regeneration with direct transformation. Prefer regeneration when a
canonical source and affordable deterministic generator already own the result.
Prefer direct transformation when regeneration is unavailable or materially
more expensive and contract-relevant equivalence can be verified.

## Place Temporary Work

Follow an existing project scratch convention first. Otherwise:

- put helper code and lightweight evidence under the owning project or
  worktree root at `tmp/<task-slug>/`;
- use an independently managed monorepo subproject's own
  `tmp/<task-slug>/` only when that subproject truly owns the task;
- keep formal deliverables in their explicit output location; a deliverable is
  not a cleanup candidate merely because a temporary helper produced it;
- use output-adjacent staging when atomic publication, same-filesystem rename,
  or large-artifact capacity requires it;
- keep each worker's temporary files in its owning worktree and do not share
  mutable scratch state across workers.

Do not scatter temporary helpers through source directories, silently edit
`.gitignore` to hide them, or default traceable work to a host-global temporary
directory. Read `~/.codex/HOST_LOCAL.md` only when host-specific storage or temp
behavior matters.

## Execute And Verify Proportionately

- Keep source inputs immutable by default and write a new output. Treat an
  in-place rewrite, overwrite, or source deletion according to its destructive
  and recovery boundary.
- Reuse stable project utilities when appropriate, but do not add a production
  API solely to make a one-off helper easier to write.
- Use a dry run, small sample, staged output, or manifest when it materially
  reduces risk. Do not require every mechanism for every task.
- Verify the actual contract with suitable counts, keys, schemas, checksums,
  ordering checks, semantic comparisons, sampled reads, or consumer checks.
  Do not substitute invented invariants for the requested behavior.
- Treat temporary code as real task-owned code: make inputs explicit, fail
  safely, avoid secrets, and keep side effects bounded.
- Follow global authorization for package installation, large artifacts,
  destructive replacement, heavy resources, and long-running execution. This
  skill does not launch or monitor such work by itself.

## Retain And Clean By Ownership

Use the role matrix in the reference before a non-trivial cleanup.

- Preserve small, non-sensitive helpers, manifests, or evidence when they make
  the result reproducible or auditable.
- Remove task-owned staging, cache, partial output, and sensitive intermediate
  files after their verification value ends.
- Never delete a formal deliverable, canonical input, pre-existing file, or
  item of unknown provenance merely because it is under `tmp/`.
- Clean exact task-owned paths; do not clear an entire project `tmp/`, system
  temp directory, or generic cache by inference.
- Treat preservation and Git tracking separately. Do not stage or commit a
  retained helper without explicit authority.
- Reconsider promotion when the helper becomes a normal repeated workflow. Move
  it into the narrowest durable migration, operations, or product surface only
  with tests, ownership, and support expectations appropriate to that surface.

## Report The Handoff

Keep the record conversational unless a multi-run, long-running, or handoff
contract needs a small manifest:

```yaml
temporary_work:
  steady_state_change:
  transition_work:
  owning_root:
  helper:
  canonical_inputs: []
  deliverables: []
  staging: []
  verification:
  retained: []
  removed: []
  remaining_risk:
```

Report exact paths, command and environment owner, transformation boundary,
verification evidence, retention result, and anything not run. A helper's pass
does not prove the overall task complete.

## Collaborate Without Taking Domain Ownership

- `personal-brainstorms` resolves a consequential durable-versus-temporary
  choice when the evidence does not decide it directly.
- `personal-repo-intake` resolves an unclear root, worktree, project convention,
  dirty-state overlap, or output owner.
- Domain skills such as `personal-evidence-debugging`,
  `personal-context-optimization`, `personal-docs-sync-light`, and
  `personal-code-simplifier` own the hypothesis, evidence use, docs patch, or
  cleanup contract; this skill owns only helper and temporary artifact
  boundaries.
- `personal-test-first-changes` owns the durable behavior change and its focused
  evidence. A temporary converter does not replace a regression test for the
  new steady state.
- `personal-subagent-boundaries` owns delegation, while
  `personal-multiline-coordination` owns worktrees and shared immutable data
  bindings.
- Global `AGENTS.md` owns long-job, resource, sensitive-data, and destructive
  authorization. `personal-long-job-status` may later provide an explicitly
  requested one-shot status check.
- `personal-risk-verification` owns the only final completion verdict, and
  `personal-branch-finish` owns later Git readiness and untracked-file handoff.

See [source notes](references/source-notes.md) for local provenance, official
Codex design evidence, baseline observations, and deliberate deviations.
