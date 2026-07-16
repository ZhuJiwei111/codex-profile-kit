# Serial-Phase Plan Contract

Read this reference before initializing, adopting, resuming, correcting, or
repairing a managed planning set.

## Active Layout

Use one project-root coordinator and one trio per ordered phase:

```text
<canonical-root>/
├── task_plan.md
└── .planning/
    ├── plans/
    │   ├── <phase-id>/
    │   │   ├── task_plan.md
    │   │   ├── findings.md
    │   │   └── progress.md
    │   └── <next-phase-id>/
    ├── snapshots/               # only approved correction/archive evidence
    └── archive/                 # only closed terminal plans
```

Do not create root `findings.md` or `progress.md`, nested phase directories,
parallel child plans, active pointers outside root `task_plan.md`, or another
active copy. Formal deliverables and evidence stay in their owning project
locations and are linked from the phase trio.

The `.planning/` top level contains exactly `plans/`, `snapshots/`, and
`archive/` when those namespaces exist. Each phase directory contains exactly
`task_plan.md`, `findings.md`, and `progress.md`. Reject `_repo`, packet,
generation, staging, or transaction leftovers only through their precise
legacy names: `_repo`, `.staging`, `TRANSACTION.md`, `transactions`, exact
`PACKET.md`, `generation-history`, numeric `generation-<digits>`, and
`gNNNN`/`gNNNN-*`. Do not reject an ordinary domain filename merely because it
contains `packet`,
`generation`, or `history`. `snapshots/` and `archive/` may contain ordinary
evidence files and directories, but every managed subtree is no-follow: reject
symlinks, multiply linked regular files, special files, and path escape
anywhere below these namespaces.

## Canonical Root And Writer

Resolve the root in this order:

1. Use an explicit root only when it belongs to the task-owned cwd or worktree.
2. In Git, use `git rev-parse --show-toplevel` from that cwd.
3. Outside Git, use an unambiguous current workspace root.
4. Use bounded core inspection and ask when multiple roots remain plausible.

Never substitute a Git common directory, another worktree, home directory, or
skill directory. Store the resolved current-host absolute path as
`canonical_root` in the root and every phase `task_plan.md`.

The coordinator in that worktree is the sole authoritative writer. Workers and
executors return evidence and a recommended outcome. They do not update the root
file or a phase trio, even when they can see the same files.

## Root Schema

Root `task_plan.md` uses only this frontmatter shape:

```yaml
---
planning_owner: personal-planning-with-files-zh
schema_version: 2
plan_kind: project
plan_role: root
plan_id: project-roadmap
plan_status: active
canonical_root: /absolute/project/root
phases: [phase-01-foundation, phase-02-delivery]
active_phase: phase-01-foundation
---
```

Use lowercase ASCII letters, digits, and hyphens for `plan_id` and phase IDs;
keep each between 3 and 64 characters. Phase IDs are unique and their list order
is authoritative. Omit `active_phase` while the project is draft or closed;
an explicit `active_phase: null` is invalid because the field must be absent.

The root body contains only:

- global goal, scope, and non-goals;
- global acceptance;
- the ordered phases and their bounded purpose;
- approved global decisions and constraints; and
- overall status plus the active pointer.

Do not copy phase steps, evidence, commands, progress, or phase-specific risks
into the root.

## Phase Trio Schemas

Each phase `task_plan.md` uses:

```yaml
---
planning_owner: personal-planning-with-files-zh
schema_version: 2
plan_kind: phase
plan_id: project-roadmap
phase_id: phase-01-foundation
plan_role: task_plan
phase_status: active
canonical_root: /absolute/project/root
---
```

Its body owns the phase goal, scope, non-goals, acceptance, ordered steps,
dependencies already available from earlier phases, risks, and close condition.

`findings.md` uses:

```yaml
---
planning_owner: personal-planning-with-files-zh
schema_version: 2
plan_kind: phase
plan_id: project-roadmap
phase_id: phase-01-foundation
plan_role: findings
evidence_cutoff: unverified
---
```

Keep reusable evidence and decisions, not a transcript. Label material entries
`observed`, `user-provided`, `inferred`, `unverified`, or `invalidated`.

`progress.md` uses the same common identity fields with
`plan_role: progress`. Its body owns current execution state, changed files,
commands and exit status, fresh verification, blockers, handoff, and next
authorized action.

All three files must agree on the shared identity fields: owner, schema, plan
ID, and phase ID. Each file declares its own specified role (`task_plan`,
`findings`, or `progress`); those role values are intentionally different. Only
phase `task_plan.md` owns `phase_status` and `canonical_root`.

## Serial-State Invariants

Use only `draft`, `active`, and `closed`.

| Root status | Required phase state |
| --- | --- |
| `draft` | No active pointer; every phase is draft. |
| `active` | Exactly one pointer target is active; every earlier phase is closed; every later phase is draft. |
| `closed` | No active pointer; every phase is closed. |

The root phase list and the phase directories must match exactly. An unlisted
phase directory, missing trio, duplicate root findings/progress, second active
phase, stale pointer, or mismatched identity is invalid. A blocked phase remains
active with a blocker in `progress.md`; do not invent another state.

## Read-Only Validator

Run:

```bash
python3 <skill-dir>/scripts/validate_plan_state.py \
  --canonical-root /absolute/project/root \
  --operation inspect \
  --json
```

Operations are `inspect`, `init`, `resume`, `correct`, `archive`, and
`successor`. `--record` may select the canonical root or one listed phase
directory, but the validator always checks the whole project state.

Use `inspect` for read-only inspection, ordinary content updates, phase switch,
project closure, and handoff. Use `resume` only for explicit resume. Use the
operation matching `init`, `correct`, archive preflight, or successor preflight;
the validator never performs the mutation.

The validator:

- opens the canonical root from filesystem `/` one no-follow directory
  component at a time, pins that descriptor, and reopens and compares the whole
  anchor chain during verification;
- opens managed paths from that pinned canonical-root descriptor and traverses
  directories with no-follow semantics;
- rejects path escape, duplicate truth, invalid pointers, non-serial states, and
  files or directory identities that change during the read;
- allows only the three owned `.planning` namespaces, an exact trio per phase,
  and single-link, symlink-free ordinary evidence under historical namespaces;
- reports source hashes for approval binding;
- treats an empty safe root as `initializable` only for `init`; and
- never writes, repairs, chooses content, or grants authority.

Run it before binding a write preview, rerun the same operation and selector
immediately before every approved write, and compare the exact reported source
path set and `source_hashes`. A mechanically valid result does not prove
semantic correctness, current dynamic facts, writer ownership, or approval.
Internally, before returning, the validator reopens the root anchor chain,
re-resolves each controlled path, and sequentially rechecks identities and
hashes. This detects bounded drift and atomic replacement of one file or
directory; it does not provide a cross-file atomic snapshot or expose a public
path-identity API.

## Adoption And Collisions

All planning files remain user-owned. Handle existing state as follows:

| State | Required behavior |
| --- | --- |
| All managed paths absent | Show an exact draft before creating it. |
| Only root or only some phase files exist | Treat as partial; inspect and propose repair. |
| Unmarked root planning files | Treat as user-owned; do not enroll automatically. |
| Compatible managed serial plan | Update only for an explicit request concerning it. |
| Root findings/progress or another detailed plan copy | Stop on duplicate truth. |
| `_repo`, packet/generation, staging, transaction, or other namespace residue | Stop; migrate or remove only under a separately approved repair. |
| Same ID with different content | Stop; never merge by filename alone. |
| Symlink, path escape, or unclear writer | Stop without writing. |

Migration from an older hierarchy is a separately approved rewrite. Show the
old records, exact new root and ordered phases, content mapping, omissions, and
verification. Do not preserve obsolete hierarchy or initialization selectors in
new metadata.

## Restart Check

On explicit resume, read the root first and then the selected phase trio. The
bounded read must answer:

- What global outcome and acceptance govern the project?
- Which ordered phase is active, and are serial states consistent?
- What does this phase own and exclude?
- Which evidence and decisions remain reliable, with what cutoff?
- What is blocked or unverified?
- What was last checked, and what is the next authorized action?

Recheck worktree state, paths, dynamic facts, and relevant evidence. Recorded
success never replaces fresh verification.
