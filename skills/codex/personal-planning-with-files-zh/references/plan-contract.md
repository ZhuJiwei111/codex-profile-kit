# Plan Contract

Use this contract when creating, adopting, migrating, repairing, or resuming a
managed planning set.

## Contents

- Active layout
- Canonical root and writer
- Read-only validator
- Explicit root rebind
- Identity and metadata
- Planning levels and lineage
- Ownership, collisions, and legacy adoption
- File responsibilities
- Restart check

## Active Layout

Use this project-local layout:

```text
<canonical-root>/
├── task_plan.md                         # optional repo-plan active trio
├── findings.md
├── progress.md
└── .planning/
    ├── _repo/
    │   ├── history/
    │   │   └── g0001-YYYYMMDD-<slug>/
    │   │       ├── SNAPSHOT.md
    │   │       ├── task_plan.md
    │   │       ├── findings.md
    │   │       ├── progress.md
    │   │       └── corrections/         # only when needed
    │   └── .staging/                    # approved transactions only
    ├── plans/
    │   └── <plan-id>/
    │       ├── task_plan.md
    │       ├── findings.md
    │       ├── progress.md
    │       ├── history/
    │       └── .staging/
    └── archive/
        ├── plans/
        │   └── <plan-id>/
        └── repo/
            └── <repo-plan-id>/
```

Keep task-plan directories physically flat. Use metadata for hierarchy. Do not
create recursive parent/child directory trees, an active pointer, a global
registry, or a second active copy.

## Canonical Root And Writer

Resolve the root in this order:

1. Use an explicit root only when it belongs to the task-owned cwd or worktree.
2. In Git, use `git rev-parse --show-toplevel` from the task-owned cwd.
3. Outside Git, use the current workspace root only when it is unambiguous.
4. Use bounded `personal-repo-intake` inspection when multiple roots remain.
5. Ask rather than choosing between plausible roots.

Never use `--git-common-dir`, a main checkout, a home directory, a skill
directory, or another worktree as a fallback.

Store the resolved absolute current-host root as `canonical_root`. This is
per-plan identity and ownership state, not a host fact for `HOST_LOCAL.md`. A
tracked planning set that appears in another worktree therefore fails root
validation instead of becoming another writable copy. Rebind a moved project
only through the explicit operation below.

Assign one canonical writer and worktree per plan:

- The coordinator worktree owns a repo plan.
- The task-owned worktree owns a bounded task plan.
- Workers return evidence through handoff and intake.
- Do not write a plan from another worktree, even when Git contains the same
  files there.

Before writing, report the canonical root and every target path.

## Read-Only Validator

Validate one explicitly selected managed record with the bundled standard-
library script:

```bash
python3 <skill-dir>/scripts/validate_plan_state.py \
  --canonical-root /absolute/current/root \
  --record /absolute/current/root/.planning/plans/<plan-id> \
  --check-lineage \
  --json
```

For the optional repo plan, pass the canonical root itself as `--record`. Pass
`--for-initialization` only when evaluating a snapshot or terminal archive as
an initialization source; using it with an active or staging record is invalid.
The script requires explicit paths: it does not discover or choose the primary
record, modify files, repair state, or grant authority.

Run it:

- before resuming or mutating an existing managed record;
- before binding a lifecycle preview to source hashes;
- immediately before an approved transition;
- after a transition, against every new active or frozen record it created;
- when a moved record may require rebind.

Interpret the result as follows:

| Status | Exit | Meaning |
| --- | ---: | --- |
| `valid` | 0 | The checked mechanical contract passed. |
| `stale` | 1 | Evidence or binding needs review; do not write. |
| `incomplete` | 1 | A partial transaction or unresolved staging state exists. |
| `invalid` | 1 | The selected record violates the managed contract. |
| `invocation_error` | 2 | The requested root or record could not be inspected. |

JSON output distinguishes `inspection_root` from
`recorded_canonical_root` and includes the selected record type, plan id,
generation, frozen `record_trust` or staging `transaction_phase` when
applicable, current trio hashes, issues, and `needs_rebind`. It opens controlled
files without following symlinks, derives frontmatter and SHA-256 from the same
read, and rejects a result when the files change during validation.

Use `hash_binding_scope` exactly:

| Scope | Permitted use |
| --- | --- |
| `standard` | Bind an ordinary approved transition to the returned trio hashes. |
| `rebind-preview-only` | Bind only a rebind preview when the sole non-info issue is `canonical_root_mismatch`. |
| `none` | Do not use the returned hashes as an approval shortcut. |

The rebind exception never authorizes resume, recovery, or another lifecycle
operation. `incomplete + needs_rebind` must return `none` and keeps both gates
closed.

A successful result does not prove semantic correctness, current writer
ownership, approval, or dynamic facts; check those separately. Do not add
`--fix` behavior or a writable transaction manager without a separately
approved design supported by repeated operational failures.

The optional lineage scan does bounded discovery of frontmatter and frozen
control metadata under managed root, task-plan, history, and terminal-archive
paths. It never loads other plan bodies or selects a plan to resume. An unmarked
root `task_plan.md` remains user-owned and is not silently enrolled. An
unmarked, unreadable, partial, or symlink-crossing record inside a managed
`.planning/` namespace is a problem to resolve, not something to normalize
automatically.

## Explicit Root Rebind

`needs_rebind: true` is a stop condition, not permission to rewrite metadata.
Use rebind only for a genuine project move or an explicitly transferred
canonical worktree. A copied checkout with another active writable record is
not a move and must not become a second writer.

Before requesting approval, show:

- plan id, generation, lifecycle, and current canonical writer;
- recorded old root and proposed resolved absolute new root;
- whether the state was moved, copied, restored, or is uncertain;
- whether the old root and another writable copy still exist on this host;
- selected record path, all target files, and current trio hashes;
- Git worktree or non-Git workspace evidence for the new ownership boundary;
- unfinished staging, worker, parent-plan, job, or handoff state;
- the exact `canonical_root` metadata change and `progress.md` rebind entry;
- facts that remain unverified because the old location is unavailable.

Wait for explicit approval bound to the plan id, generation, source hashes, old
root, new root, selected record, and intended writer. Silence, a resume request,
or merely opening the project at the new path is not approval.

After approval, update only the selected active record's `canonical_root` and
the approved progress entry. Do not rewrite frozen snapshots or archives: their
historical root is provenance. Re-run the validator at the new root and confirm
single-writer ownership before any other plan update. If the old writable copy
cannot be retired within the approved scope, stop and use a handoff or a new
plan instead of creating ambiguous authority.

If `needs_rebind` and `incomplete` occur together, do not treat rebind as
transaction recovery and do not rewrite staged metadata to make it pass. When
the old root remains available, reconcile or abort the approved transaction
there before moving. If the project has already moved, use one explicitly
approved recovery path:

1. Roll back or abort the old transaction at its current physical paths, remove
   only the known staging or partial-history artifacts covered by that approval,
   revalidate until only `canonical_root_mismatch` remains, then preview and
   approve rebind; or
2. Preserve the old transaction as recovery evidence, abort it explicitly,
   rebind the active plan, then create a fresh transaction with a new txid,
   current absolute paths, fresh hashes, and a new preview.

Never silently rewrite the old staged trio or `TRANSACTION.md`; its paths and
hashes are part of the prior approval record.

## Identity And Metadata

Use lowercase ASCII letters, digits, and hyphens for a stable `plan_id`. Keep it
between 3 and 64 characters and do not reuse it for a different plan.

Let `task_plan.md` own canonical metadata. For a task plan, use:

```yaml
---
planning_owner: personal-planning-with-files-zh
schema_version: 1
plan_kind: task
plan_id: dense-model-smoke
plan_role: task_plan
plan_status: draft
generation: 1
canonical_root: /absolute/task-owned/worktree
evidence_cutoff: unverified
root_plan_id: repo-foundation-v0
parent_plan_id: train-ready-pipeline
predecessor_plan_id: dense-model-smoke-v0
initialized_from: archive:dense-model-smoke-v0#c0001
---
```

Omit optional lineage fields instead of writing empty values.

Use one exact `initialized_from` selector:

| Form | Meaning |
| --- | --- |
| `archive:<plan-id>#original` | Original controlled terminal archive. |
| `archive:<plan-id>#cNNNN` | Archive as corrected through the named correction. |
| `snapshot:<plan-id>@gNNNN` | Controlled generation snapshot. |
| `snapshot:<plan-id>@gNNNN#cNNNN` | Corrected snapshot through the named correction. |
| `plan:<plan-id>@gNNNN` | Exact visible plan generation. |
| `packet:<packet-id>` | Explicit immutable context packet; verify it in its owning workflow. |

The lineage scan verifies local plan, archive, snapshot, and correction
selectors when requested. It preserves packet selectors as explicit external
provenance and does not search outside the canonical project root.

For a repo plan, use `plan_kind: repo` and omit `root_plan_id` and
`parent_plan_id`. Place its active trio in the project root.

Use minimal anti-crosswire metadata in `findings.md` and `progress.md`:

```yaml
---
planning_owner: personal-planning-with-files-zh
schema_version: 1
plan_id: dense-model-smoke
plan_role: findings
generation: 1
---
```

Set `plan_role` to `findings` or `progress`. All three files must agree on
`planning_owner`, `schema_version`, `plan_id`, and `generation`. Only
`task_plan.md` owns lifecycle, root, and lineage.

Use these lifecycle fields:

```yaml
plan_status: draft | active | closed
closure_status: complete | cancelled | suspended | superseded
```

Include `closure_status` only when `plan_status` is `closed`. Record blockers,
waiting, or needs-more-evidence in `progress.md`, not as lifecycle states.

## Planning Levels And Lineage

Create a bounded task plan under `.planning/plans/<plan-id>/` by default.

Create an optional repo plan only when:

- the user explicitly requests repo-wide durable planning; or
- multiple child plans have real shared constraints, dependencies, or
  integration gates.

Those conditions justify a proposal, not an automatic write. Show and obtain
approval for the exact repo-plan draft. A repo plan is a logical singleton in
the canonical coordinator worktree, not a live shared file across worktrees.

Give lineage fields one meaning each:

| Field | Meaning |
| --- | --- |
| `root_plan_id` | Current optional repo coordinator. |
| `parent_plan_id` | Current task-decomposition parent. |
| `predecessor_plan_id` | Prior plan replaced or continued by this successor. |
| `initialized_from` | Exact plan, generation, snapshot, packet, or correction used as input. |
| `generation` | Document generation within one stable plan identity. |

Before activation, reject self-links and local cycles. Report dangling local
references. Mark known cross-branch references unresolved until their target is
visible; do not silently treat them as valid.

Do not close or archive a parent or repo plan while it has active children.
First close, reparent, or explicitly detach those children while preserving
historical lineage through `predecessor_plan_id` or `initialized_from` where
applicable.

The child plan owns detailed task state. The parent owns dependencies,
integration decisions, and a dated `last_reported` rollup with the source plan
and generation. A parent rollup never overrides newer child evidence.

## Ownership, Collisions, And Legacy Adoption

All planning files remain user-owned. A management marker identifies a workflow
contract; it does not transfer ownership or grant permission.

Handle path state as follows:

| State | Required behavior |
| --- | --- |
| All three absent | Create only an explicitly requested draft at the approved level. |
| One or two present | Treat as partial; inspect read-only and do not auto-complete. |
| Three unmarked files | Treat as user-owned legacy state; propose adoption or migration. |
| Compatible managed trio | Update only for an explicit request concerning the same plan. |
| Inconsistent markers or generations | Stop and propose repair; do not normalize automatically. |
| Same plan id with different content | Stop; never overwrite or merge by filename alone. |
| Symlink, directory, or path escape | Stop without writing. |

Classify a legacy root trio by content:

- Adopt it as a repo plan only when it is genuinely repo-wide coordinator
  state.
- Migrate it to `.planning/plans/<plan-id>/` when it represents one bounded
  task.
- Keep it read-only and ask when it mixes roles or scope is unclear.

Never dual-write a root trio and a task-plan trio. Never create a root trio for
a single bounded task merely for compatibility.

## File Responsibilities

Use concise Chinese headings unless project conventions require otherwise.

`task_plan.md` should answer:

- What is the goal, scope, and non-goal?
- What evidence constitutes acceptance?
- What phase is current and what remains?
- Which decisions are approved?
- Which risks or decision blockers remain?
- What is the lifecycle and lineage?

`findings.md` should contain reusable evidence, not a transcript. Label entries:

- `observed`: directly verified local or primary-source evidence.
- `user-provided`: supplied by the user but not independently verified.
- `inferred`: a conclusion derived from stated evidence.
- `unverified`: a hypothesis or stale dynamic fact.
- `invalidated`: evidence known not to support its former conclusion.

Give stable IDs such as `F-001` or `E-001` only to material findings or evidence
that another plan may inherit. Do not number every note.

`progress.md` should contain current state, material actions, changed files,
commands with exit status, fresh verification, blockers, and the next
authorized action. Do not copy full logs or an exhaustive timeline.

A repo plan uses the same trio but stores only repo-wide scope, shared
constraints, child dependencies, integration gates, bounded child rollups, and
repo-level verification. Keep child-specific details in the child plan.

## Restart Check

On explicit resume, read `task_plan.md` first, then the relevant findings and
latest progress. Read an applicable repo plan only when it affects the selected
task.

The selected trio should answer:

- What is the current goal and canonical root?
- Which plan and generation are active?
- What remains and what is explicitly out of scope?
- Which decisions and evidence are still reliable?
- What is blocked or unverified?
- What was last verified, with what cutoff?
- What is the next authorized action?

Recheck Git or worktree state, paths, dynamic facts, and relevant evidence.
Recorded success never replaces fresh verification.
