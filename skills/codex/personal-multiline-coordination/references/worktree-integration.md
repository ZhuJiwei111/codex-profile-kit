# Worktrees, Project Data, And Integration

## Placement

Resolve worktree location by this precedence:

1. explicit user choice;
2. repository instructions or established convention;
3. Desktop-native worktree placement;
4. applicable host-local override;
5. repo-sibling fallback.

Fallback layout:

```text
<repo-parent>/.codex-worktrees/<repo-name>/<coordination-id>/
├── integration/
└── workers/
    ├── <line-a>/
    └── <line-b>/
```

Keep it outside the repository and outside `~/.codex`. Record the absolute path
and `location_source`; never infer ownership from a directory name alone.

## Workspace Ownership

- One active writer gets one worktree, one branch, and one canonical `cwd`.
- Two active writers never share a worktree.
- A reader is bound to a fixed revision. It needs a worktree only when its tools
  or isolation require one.
- The integration worktree is coordinator-owned. Workers never edit it.
- Existing unrelated worktrees are inventory, not automatically coordination
  lines or cleanup candidates.
- A dependent writer's worktree is created only after its required predecessor
  checkpoints are integrated and its exact base OID can be recorded.

Before use, check branch, HEAD, dirty state, interrupted Git operations, and
whether the worktree path already belongs to another task.

## Project-Local Heavy Files

Classify the project path before sharing it.

### Tracked content

Keep Git-tracked data under the repository's existing mechanism, including Git
LFS, DVC, or a project-specific fetch/materialization workflow. Do not replace a
tracked path with a symlink.

### Ignored, immutable content

An ignored or untracked project-local file or directory may be bound into a
worker worktree with a controlled symlink when all of these hold:

- the source is inside the primary project root;
- the source itself contains no Git-tracked project content and is not the
  project root or Git metadata;
- the source already exists and is treated as immutable for the line;
- the destination is a safe relative path, currently untracked, and ignored;
- the destination does not shadow any tracked path;
- the link resolves exactly to the declared source;
- the worker sandbox can read the source;
- the line card forbids source mutation.

Record `relative_path`, absolute `source_path`, `mutability: immutable`, and
`binding: symlink` in the snapshot. A symlink does not mechanically make its
target read-only. The auditor validates declaration, path, Git, and target
invariants; enforce actual access through the worker contract or an explicitly
chosen filesystem mechanism.

### Mutable content

Do not share writable data, caches, logs, outputs, databases, or lock-bearing
directories through a symlink. Give each line its own path. Declare output paths
so the scheduler can prevent collisions.

Cleanup removes only an approved link or worktree. It never deletes the source
project data.

## Checkpoint And Integration

Workers hand off without committing. Under an exact integration grant, the
coordinator:

1. verifies the worker report, line diff, ownership, and focused tests;
2. confirms the line branch still descends from `target_base_oid`;
3. stages only accepted task-owned paths;
4. creates one line checkpoint commit on the worker branch;
5. records its source OID;
6. integrates through the dedicated integration worktree, normally with
   cherry-pick;
7. records the resulting integrated OID and method;
8. runs appropriate integration checks before accepting successors.

The grant must name allowed lines and stage scope. It must not become a generic
`git add -A`, final commit, merge, push, PR, or publication permission.

### Conflict-resolved provenance

Record the mechanism that proves the final integration, not merely the command
that started it. When `cherry-pick` or `rebase` stops for a conflict and the
coordinator stages any manual resolution before continuing:

- set the integration record to `method: manual`;
- record the resulting integration commit as `integrated_oid`;
- keep the source checkpoint reachable through a full named
  `preservation_ref`, such as its worker branch;
- verify the resolved content, final diff, requirements, and integration HEAD
  directly; and
- retain the auditor's equivalence warning instead of relabeling the record to
  satisfy patch-ID validation.

The source and integrated commits may express the same intended change while
still producing different stable patch IDs because their surrounding context
differs. A successful `cherry-pick --continue` does not restore mechanical
patch equivalence after a manual resolution.

## Conflict Routing

- Tiny, deterministic, fully understood conflict: coordinator resolves under
  the integration grant.
- Ordinary bounded conflict needing independent analysis: managed subagent.
- Substantive conflict requiring implementation rework or multiple turns:
  Desktop-visible worker in its own line/worktree.
- Cross-line architecture or product choice: ask the user a normal targeted
  question, using `personal-brainstorms` when consequential. Route to
  `personal-grilling` only when the user explicitly invokes
  `$personal-grilling`.

Do not use a conflict worker merely because a conflict exists. Choose the
smallest surface that preserves ownership and evidence.

## Cleanup Eligibility

A worker worktree is only a cleanup candidate when:

- the line is closed with a terminal coordinator decision;
- the worker is stopped or reported;
- the worktree is clean;
- its checkpoint is integrated with a valid source-to-result OID record, or is
  preserved by a named Git ref;
- no active line depends on its mutable outputs;
- the exact worktree is covered by a cleanup grant.

Cleanliness alone never proves disposability.
