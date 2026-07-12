# Durable Versus Temporary Work

Use this reference when a one-off request could either become maintained code
or remain a bounded helper, when placement is unclear, or when transformation
and cleanup risk require an explicit contract.

## Contents

- [Choose The Surface](#choose-the-surface)
- [Use The Hybrid Pattern](#use-the-hybrid-pattern)
- [Choose The Owning Root And Paths](#choose-the-owning-root-and-paths)
- [Classify Artifact Roles](#classify-artifact-roles)
- [Lock A Transformation Contract](#lock-a-transformation-contract)
- [Verify Without Inventing Semantics](#verify-without-inventing-semantics)
- [Retain, Clean, Or Promote](#retain-clean-or-promote)

## Choose The Surface

| Situation | Default surface | Reason |
| --- | --- | --- |
| One direct command, no created helper or artifact | Ordinary task execution | A temporary workflow would add ceremony without ownership value |
| Explicitly one-off local conversion, repair, evidence pass, or post-processing | Temporary helper | Transition logic has no supported future consumer |
| Future default changes and existing artifacts need conversion | Hybrid: minimal durable change plus temporary helper | Separate steady state from historical transition |
| Multiple users, environments, releases, or versions must run the migration | Dedicated durable migration or operations surface | Execution, rollback, compatibility, and support are ongoing contracts |
| Normal product behavior or user-facing capability | Maintained product code | Calling it temporary would evade durable ownership and testing |

Ask these questions only when the answer is not already known:

1. Will a normal future user or workflow need this behavior after current state
   is converted?
2. Must multiple operators, deployments, releases, or historical versions run
   it independently?
3. Does the project promise a supported CLI, rollback path, compatibility
   window, or repeatable upgrade procedure?
4. Is there already a maintained migration or operations surface that owns it?
5. Can the existing state be converted safely without changing the normal
   runtime path?

An explicit one-off request with no positive answer defaults to a temporary
helper. Do not promote code merely because the current production script is a
convenient place to put it.

## Use The Hybrid Pattern

When a generator's future default changes while existing artifacts retain the
old organization, split the work:

```text
future steady state       existing state transition
-------------------       -------------------------
change the default        temporary converter
focused behavior test     immutable old inputs
docs if contractual       new staged outputs
normal code path only     equivalence evidence
```

For example, changing a shard default from `1024` to `65536` normally means:

- change only the maintained configuration or generator behavior needed for
  future `65536`-sized shards;
- test the new steady-state default and update existing contract docs if they
  expose it;
- use a temporary repacking helper for already generated `1024`-organized
  data;
- verify loss, duplication, ordering, and boundary properties only to the
  extent that the dataset contract requires them;
- avoid adding a permanent reshard module, legacy branch, feature flag, or API
  unless future users genuinely need that capability.

The temporary helper may import an existing stable serialization or validation
utility. Do not expose a new production API solely to serve the helper.

## Choose The Owning Root And Paths

Use this precedence:

1. Follow an applicable project scratch convention.
2. Otherwise use `<owning-worktree-root>/tmp/<task-slug>/`.
3. In a monorepo, use `<subproject-root>/tmp/<task-slug>/` only when the
   subproject has an independent environment, instructions, build, or lifecycle
   and fully owns the task.
4. Put a large or atomically published staging output beside its formal output
   when same-filesystem rename or storage capacity requires it.
5. Use a host-global temporary directory only for pure throwaway material with
   no audit or reattachment value and after confirming host behavior.

Do not equate helper location with deliverable location:

```text
repo/
  tmp/reshard-1024-to-65536/
    repack_shards.py
    manifest.json

data/
  dataset-old/                 canonical input
  .dataset-new.part-<run-id>/  output-adjacent staging
  dataset-new/                 formal deliverable
```

Use a descriptive stable task slug. Add `runs/<run-id>/` only when repeated
attempts need separate evidence; do not add hierarchy for a single small run.
Never clean a parent `tmp/` merely because the task subdirectory is disposable.

## Classify Artifact Roles

| Role | Examples | Default treatment |
| --- | --- | --- |
| Canonical input | Existing dataset, source manifest, original artifact | Keep immutable; change or delete only under an explicit recovery contract |
| Formal deliverable | Converted dataset, requested report, migrated database | Preserve at its declared output path; never treat as cleanup merely because a helper produced it |
| Traceable helper or evidence | Converter, parser, manifest, count summary | Preserve when small, non-sensitive, and useful for audit, reproduction, or retry |
| Staging or partial output | `.part`, temporary database, incomplete shard set | Keep isolated; remove after success or according to the failure-recovery contract |
| Cache or scratch | Derived index, decoded chunk, local tool cache | Remove after its task-owned verification value ends |
| Sensitive intermediate | Decrypted data, auth dump, secret-bearing log | Avoid creating; never report contents; remove promptly through the authorized mechanism |
| Pre-existing or unknown provenance | Another task's file, user notes, unexplained cache | Preserve and exclude from cleanup until ownership is established |

A path under `tmp/` does not prove that the current task owns it. A path outside
`tmp/` does not prove that it is durable. Use provenance and the declared role.

## Lock A Transformation Contract

Before a non-trivial transformation, lock only facts that affect correctness or
recovery:

- exact input identities and intended order;
- output format, location, name, and existing-output policy;
- whether the transformation must preserve bytes, records, keys, order,
  metadata, or only higher-level semantics;
- allowed normalization and intentionally changed properties;
- expected scale, storage headroom, environment, and resource scope;
- interruption behavior, resumability, staging, publication, and rollback;
- success signals and the fate of old inputs after acceptance.

Keep canonical inputs immutable and create a new output by default. Use an
in-place rewrite only when it is explicitly required, recovery is defined, and
the authorization covers the destructive surface.

For atomic publication, create staging on the same filesystem as the formal
output and publish only after verification when the platform and artifact type
support that operation. Do not call a multi-file directory swap or cross-device
copy atomic without evidence. Check capacity for both staging and retained
inputs before a large conversion.

## Verify Without Inventing Semantics

Choose evidence from the actual contract:

- counts or key sets for loss and duplication;
- schemas or parsers when syntactic validity is part of the contract;
- checksums when byte identity matters;
- ordering or boundary checks when consumers rely on them;
- before/after semantic summaries when representation may change;
- a bounded consumer read or sample when integration matters;
- a manifest when multiple inputs, outputs, attempts, or a handoff need durable
  provenance.

Do not require every file to parse as JSON, reject empty records, normalize
newlines, preserve metadata, or use two full passes unless the task contract or
risk justifies it. More checking is not automatically better when it changes
semantics, doubles a large workload, or creates another unsupported artifact.

Verify the steady-state and transition halves separately in a hybrid change.
The converter can prove the historical data transformation; it cannot prove the
new maintained default. The durable behavior check cannot prove existing data
was converted correctly.

## Retain, Clean, Or Promote

After verification:

- retain a small helper and manifest when rerun, audit, explanation, or failure
  recovery remains plausible and they contain no sensitive data;
- remove exact task-owned partial outputs, caches, and sensitive intermediates
  whose evidence value has ended;
- preserve canonical inputs until any separately authorized replacement or
  deletion step succeeds;
- report every retained and removed path; absence from a report is not cleanup
  authorization;
- keep retained helpers untracked unless the user separately chooses Git
  inclusion.

Promote a helper only when positive evidence establishes a normal future owner:

- repeated use is expected rather than merely possible;
- multiple users or deployments need a stable interface;
- releases or versions require a supported migration path;
- tests, documentation, compatibility, rollback, and maintenance ownership can
  be stated;
- the narrowest durable location is known.

Promotion is a new maintained-code decision, not a cleanup side effect. Route
it through the relevant design, test-first, docs, and final-verification
workflows.
