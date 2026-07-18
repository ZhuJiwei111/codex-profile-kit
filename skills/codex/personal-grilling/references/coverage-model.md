# Semantic Coverage Model

Use this reference to discover material branches. Do not turn it into a fixed
questionnaire or assume that a checked heading proves semantic completeness.

## Universal Core

Account for these dimensions for every scope:

- outcome, users, decision owners, and success evidence;
- included behavior, non-goals, priorities, and visible experience;
- inputs, outputs, data, state, invariants, and information boundaries;
- interfaces, dependencies, compatibility, and affected consumers;
- failure modes, recovery, rollback, and partial completion;
- security, privacy, permissions, abuse, and sensitive data;
- performance, resources, cost, operational ownership, and support;
- verification, rollout, migration, observability, and stop conditions; and
- assumptions, unknowns, deferrals, and residual risks.

Close a dimension compactly when evidence proves it non-material or
not-applicable. Expand it when the task, repository, answer, dependency, or risk
reveals a material branch.

## Optional Task Packs

Add only packs that fit the actual work:

- **Code, refactor, or bug fix:** current behavior, callers, compatibility,
  generated sources, tests, failure reproduction, and regression surface.
- **API, integration, or protocol:** identity, versioning, schemas, ordering,
  retries, idempotency, rate limits, partial failure, and provider fallback.
- **UI or product behavior:** user journey, states, accessibility, responsive
  behavior, copy, analytics, and progressive rollout.
- **Data, ML, or experiments:** provenance, leakage, feature lineage, sampling,
  independent units, metrics, baselines, multiplicity, reproducibility, and
  deployment skew.
- **Infrastructure, migration, or operations:** topology, capacity, secrets,
  multi-writer behavior, cutover, rollback, observability, on-call ownership,
  and disaster recovery.
- **Deletion, rename, or lifecycle:** references, caches, compatibility aliases,
  tombstones, retention, restoration, and downstream propagation.
- **Process, policy, or documentation:** audience, authority, canonical source,
  exception handling, adoption, stale-state detection, and maintenance owner.

Create a narrow task-specific pack when none of these captures a material
domain boundary.

## Ordering And Propagation

Resolve safety and irreversible choices first, then upstream choices with many
dependents, then costly or high-rework choices, and finally local reversible
details. After every answer, revisit dependent branches and acceptance evidence.

During closure, check coverage, consistency, then adversarial failure. Semantic
completeness cannot be formally proven; expose that residual limit in the final
ledger instead of compensating with more ceremony.
