# Generation Rollover

Read this reference only for generation rollover, persistent-plan compaction,
compression-seed initialization, or interrupted rollover recovery.

## Contents

- Eligibility
- Preview and approval binding
- Compression seed
- Recoverable transaction
- Interrupted transaction
- Root and task variants
- Verification

## Eligibility

Use generation rollover to continue the same plan with a new concise active
trio. Preserve `plan_id`, plan hierarchy, and canonical ownership. Increment
`generation` by one.

Propose rollover only when both conditions hold:

1. A semantic phase boundary is clear.
2. Moving closed history out of the active trio materially improves recovery
   and current-state clarity.

Useful signals include:

- More than half of the active content describes closed history.
- A phase has a stable handoff and verification cutoff.
- A bounded read no longer reveals goal, current phase, latest evidence,
  blockers, and next action.
- A new delivery slice remains inside the same goal and acceptance identity.

Line count, byte count, tool count, elapsed time, or context compaction alone
never authorizes rollover. Do not roll over an unresolved debugging chain,
active long job, incomplete worker handoff, or evidence set whose meaning is
still changing.

Revise a draft in place. Use generation rollover for an active plan or for an
approved material correction that deliberately preserves the prior generation.

## Preview And Approval Binding

Run the read-only validator against the selected active record with
`--check-lineage` before preparing the preview. Resolve any `stale`,
`incomplete`, `invalid`, or `needs_rebind` result first. Use its `source_hashes`
as the approval-bound trio hashes; do not calculate a competing hash set.

Before writing, show:

- `plan_id` and canonical root;
- source and target generation;
- SHA-256 of all three source files;
- history target path;
- the semantic boundary and rollover reason;
- an `inherit | compress | history-only | drop-from-active` mapping;
- the exact compression seed;
- evidence cutoff and dynamic facts requiring revalidation;
- staging path and rollback behavior.

`drop-from-active` means the source snapshot retains the material; it does not
authorize deleting the only evidence copy.

Wait for explicit approval of this preview. Silence and an empty response are
not approval. Approval binds the source hashes, target generation, history
path, seed, and intended status. Run the validator again immediately before the
transaction. Any status change or source-hash change invalidates approval and
requires a refreshed preview.

## Compression Seed

Use a compact seed as transition data, never as a fourth active source of
truth:

```yaml
goal:
locked_constraints:
accepted_decisions:
verified_findings:
current_state:
open_risks:
unverified_items:
next_candidate_action:
evidence_cutoff:
```

Map it into the new trio:

| Seed content | Active destination |
| --- | --- |
| Goal, scope, constraints, decisions, acceptance | `task_plan.md` |
| Durable findings, sources, invalidations, open questions | `findings.md` |
| Current state, prior verification, blockers, next candidate | `progress.md` |

Carry old verification with its cutoff. Reclassify dynamic facts as unverified
until checked. A candidate action is not execution authority.

The seed may be derived from the current trio, a conversation compression, or
an immutable context packet. Verify every source before promotion. Once the new
trio is published, it remains the only active planning truth.

Store the seed and carry-forward mapping in the snapshot control record so a
future reader can explain the transition without treating the seed as active
state.

## Recoverable Transaction

Use a plan-local staging directory:

- Task plan: `.planning/plans/<plan-id>/.staging/<txid>/`
- Repo plan: `.planning/_repo/.staging/<txid>/`

The staged trio uses the target generation. Use this read-only-validator
control schema; it does not create or advance the transaction:

```yaml
---
planning_owner: personal-planning-with-files-zh
schema_version: 1
record_type: plan-transaction
operation: generation-rollover
txid: tx-rollover-g0001-g0002
plan_kind: task
plan_id: dense-model-smoke
source_generation: 1
target_generation: 2
canonical_root: /absolute/task-owned/worktree
phase: staged
seed_digest: <sha256>
source_record: /absolute/task-owned/worktree/.planning/plans/dense-model-smoke
history_record: /absolute/task-owned/worktree/.planning/plans/dense-model-smoke/history/g0001-20260711-phase-one
source_hashes:
  task_plan.md: <sha256>
  findings.md: <sha256>
  progress.md: <sha256>
---
```

Use `operation: generation-correction` only for an approved corrected-
generation transition. Keep the transaction phase synchronized with the
evidenced filesystem state:

| Phase | Required state |
| --- | --- |
| `staged` | Source still matches bound hashes; history target is absent. |
| `snapshot-published` | Source still matches; controlled history matches source hashes. |
| `active-published` | History matches source; active trio matches the staged target. |
| `verified` | Published mechanics still match and event-specific verification was recorded separately. |

Every path is a normalized current-host absolute path under the canonical
root. A phase change is part of the approved transaction, not authority for a
new operation. The validator checks the same filesystem invariants for
`verified` and `active-published`; it does not prove semantic or external test
evidence merely because the phase label says `verified`.

After approval:

1. Confirm the canonical writer, root, source generation, and bound hashes.
2. Stop if another writer is active or an unresolved staging transaction
   exists.
3. Create the staging trio and a `TRANSACTION.md` containing operation, txid,
   source hashes, target generation, paths, seed digest, and current phase.
4. Validate the staged files, roles, target generation, and restart check.
5. Copy the source trio exactly into the target history directory.
6. Write `SNAPSHOT.md` beside the frozen trio.
7. Recompute the snapshot hashes. They must equal the approval-bound source
   hashes.
8. Publish the staged trio to the canonical active paths.
9. Verify the stable plan id, target generation, roles, lifecycle, lineage,
   active content, and snapshot control.
10. Remove staging only after successful verification.

Use the validator on the staged record after `TRANSACTION.md` and the staged
trio exist. After publication and staging cleanup, validate both the active
record and the new snapshot. The active record is expected to report
`incomplete` while non-empty staging still exists; never hide that intermediate
state by weakening the validator.

The active-record check detects non-empty staging and structurally partial
history entries. Full hash, identity, trust, and transition validation requires
passing the new snapshot itself as the explicit `--record`.

A structurally partial history target is `incomplete`. A complete existing
target whose identity or hashes conflict with the transaction is `invalid`.
Do not collapse those cases into one generic collision.

For generation `N`, use a path such as:

`history/gNNNN-YYYYMMDD-<boundary-slug>/`

Use the plan-local `history/` for task plans and `.planning/_repo/history/` for
the optional repo plan.

Use this minimum snapshot control:

```yaml
---
record_type: generation-snapshot
record_trust: valid
plan_id: dense-model-smoke
generation: 1
target_generation: 2
created_at: 2026-07-11T00:00:00Z
source_hashes:
  task_plan.md: <sha256>
  findings.md: <sha256>
  progress.md: <sha256>
---
```

Follow it with the rollover reason, seed, carry-forward mapping, evidence
cutoff, and correction index. The frozen triad remains byte-for-byte equal to
the approved source.

Normal rollover preserves the active lifecycle. For a material correction, set
the target status exactly as approved; do not infer reactivation from the
correction alone.

## Interrupted Transaction

Treat `.staging/`, a partial history directory, or mismatched generations as an
unfinished transaction. Do not perform ordinary plan updates until reconciled.
Confirm the condition with the validator before choosing a recovery action, and
run it again after the approved recovery completes.

Inspect:

- `TRANSACTION.md` phase;
- current active hashes;
- snapshot hashes;
- staged trio;
- target generation and paths.

Then choose only a state-supported action:

- If the source remains unchanged and staged state matches the approved
  transaction, finish it idempotently.
- If publication is partial, restore the entire source trio from the verified
  snapshot before any new proposal.
- If no active replacement occurred, remove only the known staging data after
  reporting the aborted transaction.
- If source state changed, hashes conflict, or provenance is unclear, stop and
  request a new decision.

Exact rollback to the verified pre-transaction trio is part of the approved
operation. Do not use recovery as authority for a new plan, correction, or
scope change.

## Root And Task Variants

A task rollover changes only its own trio and history. It does not update its
parent or root plan automatically. Send a bounded child handoff after success;
the coordinator decides whether to update a rollup.

A repo rollover snapshots the root trio into `.planning/_repo/history/`. It
does not roll over child plans. Record their last reported plan IDs and
generations without copying their detailed content.

## Verification

Before reporting rollover complete, verify:

- all approval-bound source hashes matched;
- the snapshot is complete and controlled by `SNAPSHOT.md`;
- active files share one plan id and the target generation;
- plan hierarchy and canonical root did not drift;
- the new trio passes the restart check;
- historical evidence retains its cutoff;
- no unresolved staging files remain;
- no parent, child, archive, job, commit, or external action was inferred.
