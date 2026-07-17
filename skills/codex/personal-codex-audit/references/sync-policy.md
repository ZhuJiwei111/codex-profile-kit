# Profile-Kit Sync Policy

Use this policy only for a directional sync between the current host and the
selected `codex-profile-kit` worktree. Run the commands directly for the user;
ask only when permission, authentication, visibility, or a conflict decision
is missing.

## Shared Preflight

1. Resolve the repository, current host, direction, branch/upstream, intended
   remote, and current revision. Before Git network access, use the connection
   entrypoint documented for this host.
2. Run `git status --short` and inspect index/worktree ownership. Stop if an
   intended operation could absorb, overwrite, or publish unrelated work.
3. Resolve the project or host-documented Python 3.11+ interpreter before a
   sync command; `sync.py` imports `tomllib`. When `HOST_LOCAL.md` records a
   fallback environment, use it rather than an older system Python. CI's
   `setup-python` 3.11 is a compatibility baseline, not local execution
   evidence. In the examples below, replace `python3` with the resolved
   interpreter when necessary.
4. Use `PYTHONDONTWRITEBYTECODE=1 python3 scripts/sync.py ...` from the selected
   repository. Treat dry-run output as the exact target list for the inputs
   read by that command, not a persistent binding across commands. Do not add
   or expect a plan token or state file, and do not recreate transfer logic
   with ad hoc copies.
5. Enforce the source, secret, path, and symlink boundaries in
   [source-policy.md](source-policy.md). Stop if Git ancestry or a managed
   source changes after review.

Routine sync manages only the targets reported by the current `sync.py`. The
only migratable skill directories are canonical `skills/codex/personal-*`
assets. Do not scan source notes, reconcile admission/provenance or unrelated
lifecycle state, or add compatibility and repeated validation ceremony to the
routine sync gates.

## Outbound: Host To Repository

Use an explicit `sync up` or `sync to GitHub` request as authority for audit,
repository export, final verification, and the publication handoff. It does
not let this skill stage, commit, push, or publish. Treat a bare `export` as a
local-only request that ends after candidate review.

1. Run the read-only audit:

   ```bash
   PYTHONDONTWRITEBYTECODE=1 python3 scripts/sync.py audit
   ```

2. Export once:

   ```bash
   PYTHONDONTWRITEBYTECODE=1 python3 scripts/sync.py export
   ```

   Preserve canonical repository-only personal skills. Export may add or
   update active personal skills, but must not delete a canonical migration
   asset merely because it is absent from this host.

3. Inspect `git status --short`, the complete unstaged diff for every changed
   path, and `git diff --check`. Confirm that the candidate contains only
   intended portable assets and no secret, excluded, generated-runtime, or
   unrelated state.
4. Obtain `personal-risk-verification: supported` after the last candidate
   change. If the candidate changes afterward, rerun only the invalidated
   evidence.
5. For `sync up` or `sync to GitHub`, hand the unchanged candidate to
   `github:yeet` with repository/worktree, target revision, exact paths,
   unrelated state, remote/base/visibility intent, and
   `dependency_install_authorized: false`.

The audit executor never stages, commits, pushes, opens a pull request, changes
visibility, or installs a publication dependency. A bare audit, comparison, or
export ends locally without a publication handoff.

## Inbound: Repository To Host

Use an explicit inbound-sync request as authority for non-conflicting Git
integration and confirmed apply of the unchanged managed plan.

1. Fetch the configured upstream, classify both ancestry directions, and
   identify the exact incoming revision. Fast-forward when possible. For
   divergent but related history, use an existing repository policy only when
   it determines the integration method; otherwise ask the user to choose.
   Stop on unrelated local ownership, ambiguous or rewritten/unrelated
   history, merge conflict, unexpected remote/base, or a change requiring a
   user decision.
2. Run audit against the integrated revision:

   ```bash
   PYTHONDONTWRITEBYTECODE=1 python3 scripts/sync.py audit
   ```

3. Run one apply dry run:

   ```bash
   PYTHONDONTWRITEBYTECODE=1 python3 scripts/sync.py apply
   ```

   Review every listed destination. Require the complete
   `rules/AGENTS.portable.md` to target `~/.codex/AGENTS.md`, only
   `personal-*` skill directories to target the Codex skill root, and no
   `HOST_LOCAL.md`, `config.toml`, authentication, connection, or runtime-state
   target. Non-personal skills and host-only personal skill deletions must
   remain absent from the plan.

4. Immediately before confirm, re-identify the repository revision, profile
   candidate, and target list. If they still match the reviewed dry run, apply
   immediately; if any identity changed, return to the dry run. Do not insert
   unrelated Git ceremony between this check and confirm.

5. If the plan is unchanged and fully contained, apply it:

   ```bash
   PYTHONDONTWRITEBYTECODE=1 python3 scripts/sync.py apply --confirm
   ```

   When the plan contains changes, require a unique timestamped backup under
   the target home. The backup must contain every replaced destination,
   including the previous complete `~/.codex/AGENTS.md` when it changes, before
   the first corresponding write. An empty plan is a no-op and creates no
   backup.

6. Record the backup path and immediately run a post-apply audit:

   ```bash
   PYTHONDONTWRITEBYTECODE=1 python3 scripts/sync.py audit
   ```

   Require zero repository-to-host drift for managed targets. A host-only
   personal skill remains outside that directional drift. If apply fails, stop
   without more mutation and report whether its transactional rollback
   restored the previous state. If the later audit fails after apply succeeded,
   preserve the emitted backup and report the failed command, affected targets,
   and exact backup paths. Restore only those paths after an explicit recovery
   decision, then audit again.

## Verification And Resumption

- Use one verification pass per unchanged state. Export validation, exact diff
  review, apply dry run, and post-audit have different purposes; do not repeat
  them merely for ceremony.
- On resume, re-identify the repository revision, candidate or dry-run plan,
  worktree ownership, and first incomplete stage. Reuse still-fresh evidence.
- Stop before any action outside the selected direction, managed set, current
  host, or repository. Never infer publication from a successful export or
  infer permission to overwrite a conflict from an inbound-sync request.
