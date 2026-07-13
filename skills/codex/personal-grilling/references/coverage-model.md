# Coverage Model

Use this reference to discover decision branches before filtering questions.
It is a coverage aid, not a finite proof that no semantic branch exists.

## Contents

- [Leaf Contract](#leaf-contract)
- [Universal Core](#universal-core)
- [Task-Type Packs](#task-type-packs)
- [Branch Discovery And Ordering](#branch-discovery-and-ordering)
- [Closure Passes](#closure-passes)
- [Calibration](#calibration)

## Leaf Contract

Keep the working ledger in the conversation unless another workflow explicitly
owns persistence. Use this conceptual shape; do not print it mechanically after
every answer.

```yaml
id:
dimension:
question:
status: open | blocking | locked | assumption | deferred | not-applicable
source_type: user-decision | observed-evidence | inherited-constraint | low-risk-assumption | explicitly-deferred
source_ref:
dependencies: []
consequence:
risk_disposition: avoid | mitigate | accept | defer | not-material
reopen_condition:
```

Status rules:

- `open`: a possible material branch still needs evidence or classification.
- `blocking`: a user-owned decision is required before reliable handoff.
- `locked`: sufficient evidence or an explicit user decision resolves the leaf.
- `assumption`: a non-material, low-risk, reversible default resolves the leaf.
- `deferred`: the user explicitly moved a material leaf outside this delivery
  slice.
- `not-applicable`: evidence shows the dimension cannot affect the current
  outcome. Record the reason.

Do not use `assumption`, `deferred`, or `not-applicable` as synonyms for “not
considered.” `source_ref` may point to a user answer, file, test, command,
authoritative document, inherited instruction, or concise evidence statement.

## Universal Core

Audit every dimension. Ask the user only when the resulting leaf is material,
user-owned, and unresolved after bounded evidence collection.

| Dimension | Coverage questions |
| --- | --- |
| Goal and problem | What outcome matters, what problem causes it, and would a smaller or different intervention solve it? |
| Users and ownership | Who uses, owns, approves, operates, or is affected by the result? |
| Current evidence | What is observed now, what is inferred, what remains unknown, and which baseline will comparison use? |
| Scope and non-goals | Which systems, artifacts, users, environments, and behaviors are included or explicitly excluded? |
| Behavior | What must change, remain stable, or become visible to users and downstream consumers? |
| State and data | What state exists, where truth lives, how it changes, and what lifecycle, privacy, retention, or integrity constraints apply? |
| Interfaces and dependencies | Which APIs, files, tools, services, skills, people, or contracts connect the work to other components? |
| Constraints and resources | Which time, cost, compute, storage, environment, policy, quality, or reversibility limits are binding? |
| Security and authorization | What trust, credential, privilege, disclosure, external-action, or approval boundary applies? |
| Failure and recovery | How can it fail, how will failure be detected, what state may be partial, and how is rollback or repair performed? |
| Compatibility and migration | Which old states, versions, consumers, hosts, formats, or discovery paths must coexist or migrate? |
| Operations and handoff | Who launches, observes, decides, maintains, documents, and accepts the resulting state? |
| Acceptance | Which current evidence will prove each material requirement, and what will remain intentionally unverified? |

Check cross-cutting consequences. A choice about one dimension often opens
another: persistence changes security and migration; parallelism changes
ownership and recovery; a new dependency changes portability and acceptance.

## Task-Type Packs

Select every applicable pack. Packs add branches; they never cancel the
universal core.

### Feature, API, Or UI

- target user, job, entry point, and success path;
- empty, loading, partial, error, retry, cancellation, and permission states;
- input, output, API, schema, and backward-compatibility contracts;
- accessibility, localization, responsive behavior, and platform differences;
- persistence, concurrency, idempotency, ordering, and duplicate handling;
- telemetry, rollout, discoverability, support, and deprecation;
- abuse, privacy, and authorization boundaries;
- unit, integration, contract, and user-visible acceptance evidence.

### Code, Refactor, Or Configuration

- repository and instruction ownership, relevant dirty state, and edit surface;
- intended behavior change versus behavior-preserving cleanup;
- public interfaces, callers, config precedence, defaults, and compatibility;
- data or state transformation and failure atomicity;
- environment, dependency, generated-file, and packaging ownership;
- focused RED or preserving baseline, coupled checks, docs contract, and final
  diff evidence;
- rollout, rollback, feature flags, and cleanup of transitional paths.

### Data, ML, Or AI4Biology Experiment

- research question, biology hypothesis, claim level, and decision the
  experiment should support;
- biological entity, context, mechanism assumption, intervention, and relevant
  domain limitation;
- data provenance, cohort, sampling, inclusion criteria, labels, missingness,
  batch effects, split strategy, leakage, and confounders;
- prediction-time information boundary and feature lineage: what is available
  at inference, how the biology signal becomes an input, representation,
  target, objective, constraint, or evaluation slice, and whether target or
  test information enters feature construction;
- independent experimental unit and pseudoreplication risk: whether inference
  and statistics operate over cells, samples, donors, batches, cell types, or
  another biological unit;
- evaluation-selection boundary and multiplicity: pre-specified primary metric,
  direction, and go/no-go rule; separation of tuning, validation, and one-time
  final test; repeated test inspection; model, metric, or slice selection; and
  multiple comparisons across genes, cell types, models, seeds, or metrics;
- baselines, matched controls, positive and negative controls, ablations,
  shuffles, and alternative explanations;
- metrics, uncertainty, statistical comparison, practical significance, and
  failure thresholds;
- reproducibility, seeds, code and data versions, compute, storage, duration,
  monitoring authority, and stop criteria;
- which result changes the research or engineering decision and which broader
  claims remain unsupported.

### Workflow, Automation, Or Codex Profile

- trigger, invocation, implicit versus manual behavior, and authoritative owner;
- active, configured, enabled, trusted, cached, archived, and portable states;
- canonical source, generated mirror, sync direction, idempotency, and drift;
- single- versus multi-writer authority, concurrent writers, merge or precedence
  policy, lost-update protection, duplicate submissions, locking, and conflict
  resolution;
- deletion, rename, and tombstone propagation, including stale discovered state
  and protection against unintended host-local deletion;
- current-host facts versus machine-neutral configuration;
- public MCP versus credential-bearing or host-specific integration;
- credentials, trust hashes, project discovery, external state, and approval;
- version compatibility, schema changes, discovery paths, and upgrade policy;
- bootstrap and self-update trust root: how a clean host obtains the synchronizer,
  how its version is pinned, and how recovery remains possible when the updater
  itself breaks;
- failure reuse, backup, rollback, restore, audit, and real smoke evidence;
- cross-skill routing, lifecycle admission, maintenance, and handoff ownership.

### Migration, Deployment, Or Cutover

- inventory of old and new states, authoritative source, owners, and consumers;
- compatibility window, dual-read or dual-write behavior, version skew, and
  irreversible transitions;
- data transform, validation, checkpointing, resumability, and partial failure;
- rollout cohorts, gates, observability, performance and error budgets;
- cutover authority, rollback trigger, rollback feasibility, and retained old
  state;
- post-cutover cleanup, documentation, support, and acceptance evidence.

## Branch Discovery And Ordering

Generate candidate leaves from five sources:

1. universal core and applicable packs;
2. the user's goal, proposal, answers, concerns, and stated preferences;
3. observed repository, runtime, product, or authoritative external evidence;
4. interfaces, dependency edges, state transitions, and failure paths;
5. contradictions, second-order effects, risks, and missing acceptance proof.

Order unresolved material leaves by:

1. safety and authorization;
2. problem framing and scope;
3. decisions that determine multiple downstream branches;
4. irreversible, expensive, or migration-sensitive choices;
5. interfaces, ownership, and state contracts;
6. acceptance and operational details;
7. low-coupling implementation preferences.

A user choice closes only the stated leaf. Propagate it immediately. If an
answer selects persistence, for example, reopen security, retention,
compatibility, recovery, and ownership when those consequences are material.

## Closure Passes

### Coverage Pass

- every universal dimension has a justified status;
- every applicable pack was traversed;
- every evidence- and answer-derived branch is represented;
- every material risk has a disposition;
- every assumption, deferral, and not-applicable result has the required owner
  or evidence.

### Consistency Pass

- decisions do not contradict each other or observed evidence;
- dependency consequences have propagated;
- scope and non-goals match behavior and interfaces;
- resources and authorization support the proposed work;
- acceptance evidence can prove the actual requirements;
- late answers have not left stale closure states.

### Adversarial Pass

- challenge whether the proposed solution is necessary or merely familiar;
- run a bounded pre-mortem across safety, partial state, recovery, compatibility,
  portability, cost, operations, and ownership;
- identify attractive claims that lack evidence;
- test success, failure, cancellation, upgrade, and rollback paths;
- ask what a skeptical reviewer or future maintainer would still need to know;
- reopen each material gap before requesting explicit coverage confirmation.

## Calibration

Coverage-first does not mean maximal questioning.

- For a small, explicit, low-risk request, evidence may close most universal
  dimensions immediately. Ask only the remaining material user decision.
- For a large system, research, migration, or profile change, expect multiple
  themes and second-order branches. Do not stop because one theme is clear.
- Do not ask a discoverable fact, repeat sufficient evidence, or require a
  rationale for an unambiguous option choice.
- Do not mark a branch non-material merely to reduce interaction length.
- If the user stops, retain the open branches and label the brief incomplete.

The coverage model reduces false negatives; it cannot formally prove semantic
completeness. The user has accepted that bounded residual risk under the
three-pass and explicit-confirmation controls.
