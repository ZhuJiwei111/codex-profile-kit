---
name: personal-profile-sync
description: Manual only. Use when the user explicitly invokes this skill or requests portable-profile preview, apply, check, or deployment; an update from GitHub before applying; or commit and non-force push of a named profile change. Keep each action within the requested scope.
---

# Personal Profile Sync

Treat this Git working tree as the only editable portable source and the
current host's official `$CODEX_HOME` and Codex plugin CLI as deployment
targets. Never export active profile, plugin cache, trust, or marketplace state
back into the repository.

## Locate The Source Before Editing

Read the host's portable source path and resolve this repository's manifest.
For managed skill trees, edit `profile/skills/<name>`; plugin-owned skills use
their registered source package. Unmanaged external skills stay separate and
are not imported, renamed, or deployed by inference.

Before changing a managed skill, compare its relevant active files with the
source to identify pre-existing divergence. Before apply, reconcile preview
against the reviewed task changes. Investigate unexpected active changes;
preserve another task's work and resolve unclear ownership before overwriting.
An explicitly requested recovery of exact active edits may be reviewed and
applied to the source, but does not authorize bulk active-profile export.

## Choose The Explicit Intent

- `preview`, `apply`, or `check`: run `scripts/profile_sync.py` with the same
  Python recorded in `HOST_LOCAL.md`. It must orchestrate both the
  core profile and `scripts/plugin_sync.py` in that single command; the
  interpreter is also rendered into the host's hook definition.
- update from GitHub: inspect local state, fetch, and accept only a selected
  non-conflicting update before the combined preview/apply. Review the accepted
  diff well enough to explain its material contents.
- submit or sync to GitHub: validate and inspect the exact diff, stage only
  task-owned paths, create one factual commit, and non-force push. Do not create
  a PR unless separately requested.

The sync scripts perform no Git operation. Calling `apply` is authorization for
the scoped local profile and owned-plugin writes; it is not push authority.

## Scoped Local Deployment

Set `PROFILE_PYTHON` to the interpreter recorded in `HOST_LOCAL.md`. For an authorized skill or AGENTS change, use repeatable `--path` with exact
manifest entries on `preview`, `apply`, and `check`, for example:

```text
"$PROFILE_PYTHON" scripts/profile_sync.py preview --path skills/personal-subagent-boundaries
"$PROFILE_PYTHON" scripts/profile_sync.py apply --path skills/personal-subagent-boundaries
"$PROFILE_PYTHON" scripts/profile_sync.py check --path skills/personal-subagent-boundaries
```

Use the host's recorded Python. Scoped mode excludes configuration leaves and
plugins, accepts reviewed uncommitted source, and retains backup, lock, drift
checks and rollback. Reconcile pre-existing active/source differences before
applying. Git actions require separate authority; do not commit merely to deploy
an authorized local correction. Use exact retired manifest entries to remove a
skill; removing a source directory alone does not express retirement.

## Full Profile Release From A Reviewed Commit

For an explicitly requested full profile release, validate source and skills, run focused checks,
preview the exact diff, inspect it, stage exact paths, and, only with Git authority, create a local
factual commit before deployment. Without that authority, use scoped local
deployment for approved file/skill changes; leave a full release pending. Reusing an existing reviewed commit does not
create an empty commit.

`profile_sync.py apply` owns the manifest's managed paths, exact retirement
paths, and configured leaf keys. It must show the resolved target, back up every
replaced or retired leaf, use the official config writer, and finish with
`check`. Retiring an entire managed entry requires an explicit retirement entry. An active
managed directory mirrors the source tree, including in scoped mode. Files found
only in its installed copy appear as DELETE in preview and are backed up before
removal. Review those paths before applying.

`plugin_sync.py apply` owns only the repository's `profile-kit` marketplace,
`personal-long-job-supervisor@profile-kit`, and the exact retired selector
`personal-long-job-supervisor@personal`. Register the repository root through
the official Codex plugin CLI, install the reviewed cachebuster version, verify
it, and only then remove the retired selector. Preserve every other marketplace,
plugin, cache, credential, session, trust decision, host fact, connection
contract, and unlisted configuration. A marketplace-name collision or a
different registered root is a blocker, not permission to replace it.

When hook definitions change, keep any runner still loaded by the current task.
Use a fresh task to review `/hooks` trust and dispatch before retiring that old
runner.

When plugin source, version, skills, or MCP wiring changes, validate the plugin,
run its tests, and install it. Finish the installing task before creating the
reload-verification task. Verify the loaded skill and MCP catalog only in a
task created after the installing task has ended. A task created while the
installing task is still active can inherit its pre-install catalog and is not
fresh reload evidence.

## Report The Update

After every accepted GitHub update or applied portable-profile update, briefly
summarize the material contents of the reviewed diff. For each materially
changed managed file or logical group, name it and state the actual rules,
behavior, configuration keys, or managed entries added, removed, or revised.
Group files only when they implement the same change; omit purely mechanical
files that add no useful information.

When `AGENTS.md` changes, summarize the concrete defaults or workflow rules
that changed. When `profile-manifest.toml` changes, name the managed or retired
entries affected. Apply the same standard to skills, hooks, configuration
leaves, marketplaces, and installed plugin selectors. Do not replace this
content summary with an abstract objective such as
"updated AGENTS.md and manifest to enable project journaling." Keep the bullets
brief, but use enough of them to cover every material change. If no
profile-visible change occurred, say so.

Also report the source commit, backup path when deployment changed the target,
installed plugin version and marketplace root, checks, material unrun work, and
any remaining fresh-task action.
