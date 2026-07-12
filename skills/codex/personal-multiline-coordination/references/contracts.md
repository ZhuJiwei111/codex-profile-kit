# Coordination Contracts

Use these contracts as compact state projections, not as a second task system.
Do not put secrets, raw logs, diffs, or unrelated repository state in them.

## State Axes

Keep these axes separate:

| Axis | Owner | Values |
| --- | --- | --- |
| Coordination phase | coordinator | `designing`, `ready`, `executing`, `integrating`, `verifying`, `closed`, `blocked` |
| Line phase | coordinator | `planned`, `ready`, `executing`, `waiting_intake`, `integrating`, `verified`, `closed`, `blocked`, `cancelled` |
| Worker state | worker fact, recorded by coordinator | `queued`, `working`, `waiting`, `reported`, `stopped`, `failed`, `unavailable` |
| Worker execution status | worker fact at handoff | `scope_finished`, `boundary_reached`, `needs_input`, `cannot_continue` |
| Coordinator decision | coordinator only | `pending`, `pass`, `no-go`, `needs-more-evidence`, `blocked` |
| Workspace state | observed Git fact plus coordinator intent | `prepared`, `clean`, `dirty`, `handed_off`, `cleanup_candidate`, `preserved` |

A worker never reports `pass`. It reports evidence and a
`recommended_outcome`; the coordinator owns the decision.

## Launch Manifest

Present one manifest before explicit multiline execution:

```yaml
coordination_id: <stable-id>
repository_root: <absolute-primary-worktree-root>
target_base_oid: <verified-commit>
integration:
  branch: <dedicated-integration-branch>
  worktree: <absolute-path>
lines:
  - id: <line-id>
    objective: <bounded-outcome>
    surface: desktop_worker
    depends_on: []
    create_when: ready
    base_strategy: <target-base-or-integrated-dependencies>
    worktree: <absolute-path>
    branch: <branch>
    write_set: [<relative-path>]
    output_paths: [<relative-path>]
    resource_claims: []
    project_local_bindings: []
    stop_condition: <when-to-handoff>
    verification: <focused-evidence>
grants:
  create_visible_tasks: true
  create_non_destructive_worktrees: true
  integration: <exact-scope-or-false>
  resources: <per-line-grants-or-empty>
  cleanup: <named-conditional-scope-or-false>
```

Omit a grant rather than implying it. Name every line whose Desktop task or
worktree may be created. Authorization does not mean immediate creation:
dependent lines remain planned until their integrated base OID is known.

## Line Card

Give each worker only its bounded contract:

```yaml
coordination_id: <id>
line_id: <id>
objective: <one-outcome>
canonical_cwd: <absolute-worktree-path>
branch: <branch>
base_oid: <commit>
depends_on: []
exclusive_files: [<paths>]
allowed_actions: [<actions>]
forbidden_actions: [commit, integrate, operate_other_workers]
resource_grant: <exact-grant-or-none>
acceptance_criteria: [<criteria>]
verification: [<commands-or-checks>]
stop_condition: <handoff-boundary>
report_contract: <fields-below>
```

## Worker Report

Require:

- line id, canonical `cwd`, branch, and observed HEAD;
- files changed and outputs produced;
- commands run with exit status and concise evidence;
- unresolved risks, conflicts, and unverified items;
- whether the worktree is clean or dirty;
- the canonical handoff axes:

  ```yaml
  execution_status: scope_finished | boundary_reached | needs_input | cannot_continue
  recommended_outcome: accept | reject | needs-more-evidence
  ```

- the next event or decision needed.

The report does not authorize integration or a next stage. `rework` is a
coordinator-requested next action, not a worker outcome. `blocked` is a
coordinator decision made after intake, not a worker-reported result.

## Coordinator Intake

Record:

- worker report received and task state observed;
- Git/worktree facts independently checked;
- diff and artifact ownership assessed;
- focused evidence accepted or rejected;
- coordinator decision;
- exact missing evidence or rework if applicable;
- whether an integration grant exists;
- next ready lines or next wake event.

## Optional Snapshot V2

Use a snapshot only for machine-checkable reconciliation or handoff. It is an
ephemeral projection unless an approved file-backed plan owns it.

Every field ending in `_oid` is a full immutable Git object ID, never a branch,
tag, symbolic ref, or abbreviated hash. Only `preservation_ref` is ref-valued.

```json
{
  "schema_version": 2,
  "coordination_id": "coord-example",
  "target_base_oid": "<commit>",
  "phase": "executing",
  "lines": [
    {
      "id": "line-a",
      "phase": "executing",
      "worker_task_id": "<desktop-task-id>",
      "worker_state": "working",
      "coordinator_decision": "pending",
      "depends_on": [],
      "workspace": {
        "mode": "writer",
        "state": "dirty",
        "path": "<absolute-worktree-path>",
        "branch": "<branch>",
        "head_oid": "<commit>",
        "location_source": "repo_sibling",
        "ownership": "coordination"
      },
      "write_set": ["src/feature"],
      "resource_claims": [{"id": "gpu:0", "mode": "exclusive"}],
      "project_local_bindings": [],
      "output_paths": ["artifacts/line-a"]
    }
  ]
}
```

After integration, add:

```json
{
  "integration": {
    "workspace": {
      "path": "<absolute-integration-worktree>",
      "branch": "<integration-branch>",
      "head_oid": "<commit>",
      "location_source": "repo_sibling"
    },
    "records": [
      {
        "line_id": "line-a",
        "source_oid": "<checkpoint-commit>",
        "integrated_oid": "<resulting-commit>",
        "method": "cherry-pick"
      }
    ]
  }
}
```

`source_oid` is the worker line's immutable source checkpoint. `integrated_oid`
is the integration-branch commit recorded for that line and may become an
ancestor after later lines are applied. The integration workspace `head_oid`
is the final combined HEAD; do not substitute one per-line `integrated_oid` for
that final identity.

Only after an exact cleanup approval, add the named scope:

```json
{
  "cleanup_grant": {
    "line_ids": ["line-a"],
    "worktree_paths": ["<absolute-worker-worktree>"]
  }
}
```

For a rejected line that must still be removable, use a named
`preservation_ref` containing its `checkpoint_oid`. Never treat an unreferenced
or merely clean worktree as disposable.

## Auditor Contract

```bash
python3 scripts/audit_multiline.py <project-root> --json
python3 scripts/audit_multiline.py <project-root> --snapshot snapshot.json --json --check
```

Without a snapshot, the auditor inventories Git worktrees and interrupted
operations only. With a snapshot, it validates state, dependency, ownership,
resource, checkpoint, integration, binding, and cleanup invariants. `--check`
returns `1` for error findings and `2` when the repository itself cannot be
resolved. For cherry-pick/rebase records it also compares stable patch IDs;
manual or squash records cannot alone make a checkpoint disposable. The
auditor never enumerates Desktop tasks and never mutates Git.
