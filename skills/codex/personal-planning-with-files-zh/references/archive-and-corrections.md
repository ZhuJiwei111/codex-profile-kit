# Archive And Corrections

Read this reference only for plan closure, terminal archive, frozen-record
correction, invalidation, redaction, successor creation, or lineage impact.

## Contents

- Closure and archive
- Archive transactions
- Frozen-record controls
- Correction workflow
- Active-plan and successor paths
- Lineage impact
- Security and corruption exceptions
- Verification

## Closure And Archive

Separate lifecycle closure from storage:

```yaml
plan_status: closed
closure_status: complete | cancelled | suspended | superseded
```

Closing a plan does not move it. Archive only after a separate explicit request
or approval of the exact source, destination, and closure record.

Archive a task plan at:

`.planning/archive/plans/<plan-id>/`

Archive a repo-plan epoch at:

`.planning/archive/repo/<repo-plan-id>/`

Never reuse a plan id for unrelated work. Never overwrite an archive target.
If the target exists and is not the exact same approved record, stop.

Before closing or archiving a parent or repo plan, close, reparent, or explicitly
detach active children. Preserve historical relationships with
`predecessor_plan_id` or `initialized_from`; do not keep an archived plan as a
current coordination parent.

A terminal plan never moves back to active. Continued work uses a successor
draft with a new plan id.

## Archive Transactions

Bind approval to the plan id, canonical root, closure state, source file hashes,
history controls, destination, and intended successor relationship.

Run the read-only validator with `--check-lineage` before preparing the preview
and again immediately before writing. Use its current trio hashes for approval
binding. Resolve every `stale`, `incomplete`, `invalid`, or `needs_rebind`
result before archiving.

For a task plan:

1. Finalize the approved closure in the active trio.
2. Create `ARCHIVE.md` with closure, hashes, lineage, and
   `record_trust: valid`.
3. Verify all controlled content and that the destination is absent.
4. Move the whole plan directory, including history, within the same project
   filesystem when possible.
5. Verify the final path and remove no other data.

For a repo plan:

1. Stage the root trio, `.planning/_repo/history/`, and `ARCHIVE.md` under the
   approved archive destination.
2. Verify the staged copy and hashes.
3. Publish the archive directory.
4. Remove the root active trio and old repo sidecar only after the published
   archive verifies completely.
5. Leave no new root plan unless its exact draft and activation were separately
   approved.

If interrupted, prefer preserving both verified copies to deleting uncertain
state. Stop ordinary plan writes, identify the authoritative hashes, and resume
or roll back only the approved transaction.

Use this minimum terminal control frontmatter:

```yaml
---
record_type: terminal-archive
record_trust: valid
plan_id: dense-model-smoke
generation: 3
source_hashes:
  task_plan.md: <sha256>
  findings.md: <sha256>
  progress.md: <sha256>
---
```

Follow it with closure, lineage, destination, evidence cutoff, history index,
and correction index. After publication, validate the terminal record at its
final path. For a repo archive, also confirm that no managed active root trio
or partial sidecar remains. The archived `task_plan.md` must already have
`plan_status: closed` and a valid `closure_status`; the control file cannot make
an active trio terminal by itself.

## Frozen-Record Controls

Use `SNAPSHOT.md` for a generation history record and `ARCHIVE.md` for a terminal
archive. Store the original triad body hashes and a current trust state:

```yaml
record_trust: valid | corrected | invalidated | redacted
```

Read frozen state in this order:

1. Control file and state-change history.
2. Every applicable correction record, not only a latest pointer.
3. Original triad and referenced evidence.

Never initialize from an `invalidated` record. A `corrected` record is usable
only through the active correction chain. A `redacted` record may have missing
detail by design.

When considering any frozen record as initialization input, run the validator
with `--for-initialization`. A redacted source requires explicit completeness
review; an invalidated source must fail mechanically. The validator complements
rather than replaces review of the full correction chain.

Treat the frozen trio's `canonical_root` as historical provenance. A mismatch
with the current inspection root is informational and never a reason to rebind
or rewrite the frozen body.

Do not silently rewrite frozen triads, snapshots, or existing corrections. A
new correction supersedes an incorrect correction.

## Correction Workflow

When a serious problem is suspected but not yet approved for persistent change:

- Stop using the affected claim in current reasoning.
- Report it as temporary quarantine.
- Do not claim that an archive or snapshot has been persistently invalidated.
- Identify the proposed record, correction, and impact scope.

After explicit approval:

1. Add `corrections/cNNNN-YYYYMMDD-<slug>.md` beside the frozen record.
2. Update the control file's current trust and append a state-change entry.
3. Keep the original body and older corrections unchanged.
4. Verify that readers can discover the full correction chain.
5. Run only the approved bounded impact scan.

Run the validator before binding the correction preview and after updating the
control and correction chain. A non-`valid` trust state must have at least one
discoverable correction record named
`cNNNN-YYYYMMDD-<slug>.md`. Conversely, a correction file with
`record_trust: valid` is an incomplete control transition and must be reconciled
before the record is consumed.

Use this correction structure:

```markdown
# Correction c0001

## Detection And Source

## Affected Plan, Generation, Findings, And Evidence

## Original Problem

## Corrected Evidence

## Decision And Acceptance Impact

## Required Revalidation

## Downstream References

## Approved Disposition
```

Summarize an erroneous or sensitive claim instead of copying unsafe content.
Record which correction supersedes another correction when applicable.

Handle interrupted correction writes conservatively. A correction file that
exists without an updated control pointer still requires inspection; do not
trust only `latest_correction`. Complete the approved metadata update when its
identity and content are clear, otherwise stop.

## Active-Plan And Successor Paths

For a material error in an active plan whose goal and acceptance remain valid:

1. Temporarily quarantine the affected evidence.
2. Prepare a corrected generation and invalid snapshot control.
3. Return the plan to draft when the change affects scope, direction, or
   acceptance.
4. Obtain approval for the correction and exact target generation.
5. Publish the corrected generation through the rollover transaction.
6. Reactivate only when the revised content was explicitly approved.

For a terminal plan or an error that invalidates the core premise:

1. Add the approved archive correction and mark the frozen record invalidated.
2. Preserve the original archive.
3. Propose a successor draft with a new `plan_id`.
4. Use `predecessor_plan_id` for successor lineage, not `parent_plan_id`.
5. Point `initialized_from` to the exact corrected archive or generation.

Correction approval does not authorize successor creation, descendant edits,
implementation, or any external action unless those actions were also explicit.

## Lineage Impact

Keep impact scans bounded to the current host and canonical project root. Check
only explicit relationships:

- `root_plan_id`;
- `parent_plan_id`;
- `predecessor_plan_id`;
- `initialized_from`;
- stable inherited finding or evidence IDs.

Do not scan every Markdown file or infer dependency from similar wording.

For affected active plans, mark the evidence stale and return them to draft
only when the correction changes their direction or acceptance. For frozen
records, add correction pointers rather than changing the body. Every
descendant mutation needs its own shown scope and approval.

For another worktree, report the affected path and handoff requirement. Do not
cross the canonical writer boundary to change it.

## Security And Corruption Exceptions

Security overrides historical byte preservation:

- Remove secrets, credentials, private keys, cookies, or sensitive session data
  from every in-scope copy.
- Never repeat the removed value in a correction, hash label, log, or report.
- Record only the redacted category, affected paths, and safe remediation.
- Credential rotation remains a separate user-controlled authority boundary.

Repair verifiable corruption only from an identified trustworthy copy. Record
safe before/after hashes and provenance. Do not treat a plausible reconstruction
as verified repair.

## Verification

Before reporting archive or correction complete, verify:

- approval-bound source hashes and destination;
- closure status and absence of active unhandled children;
- complete archive controls and history;
- correction discoverability and current trust;
- original frozen bodies remain unchanged except an approved security or
  corruption exception;
- invalidated records cannot initialize new active state;
- successor, descendant, execution, and external actions were not inferred;
- no partial staging or correction transaction remains.
