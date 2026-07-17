# Profile Source Policy

Use this policy for a read-only audit and as the active-profile boundary for a
directional sync.

## Read The Smallest Safe Surface

Inspect only what is needed to establish the requested managed state:

| Source | Allowed evidence |
| --- | --- |
| `~/.codex/AGENTS.md` | Portable rules content and drift from `rules/AGENTS.portable.md` |
| `~/.codex/skills/personal-*/` | Regular-file content needed for audit or transfer |
| Portable hook and agent targets reported by `sync.py` | Exact managed files and drift |
| `codex-profile-kit` | Repository identity, Git ownership, managed sources, and exact diff |
| `~/.codex/HOST_LOCAL.md` | Only the minimum host/network fact needed to run the current task; never transfer it |

Use `sync.py audit` as the default drift source. Run
`scripts/collect_codex_profile.py --home <home>` only for an explicitly useful
safe inventory that audit does not provide. Its output is inventory evidence,
not proof of runtime health, trust, or successful activation.

## Treat Repository Membership As The Routine Skill Boundary

- Include only skill directories named `personal-*` under the canonical
  `skills/codex/` tree.
- Preserve repository-only personal skills during outbound export; they remain
  migration assets even when absent from the current host.
- Preserve host-only personal skills during inbound apply. Install or update
  canonical repository targets without treating a host-only personal skill as
  a deletion target or repository-to-host drift.
- Do not require or parse `references/source-notes.md`, admission fields, or
  provenance fields during routine audit, export, or apply.
- Route first-time admission of a newly created or externally acquired skill
  to `personal-skill-hygiene` before adding it to the canonical repository.
- Ignore active non-personal skills. Do not read their implementation for sync,
  copy them into the repository, apply repository copies over them, count them
  as drift, or delete them.

## Keep These Surfaces Out Of Apply

Never copy, replace, delete, print, or summarize secret values or runtime
state. Exclude:

- `~/.codex/HOST_LOCAL.md` and `~/.codex/config.toml`;
- `auth.json`, sessions, histories, SQLite state, attachments, logs, caches,
  memories, plugin/app/model state, and approval or trust state;
- tokens, cookies, passwords, private keys, `.netrc`, authenticated URLs,
  headers, secret environment values, OAuth state, and connector state; and
- tasks, threads, transcripts, generated archives, project outputs, datasets,
  model weights, environments, and package caches.

Templates describing excluded surfaces are manual references, not apply
targets. A profile audit may report that an excluded category exists, but must
not expose its values or convert it into transfer drift.

## Enforce Path And Symlink Containment

- Resolve the selected home and repository once; keep every source,
  destination, temporary file, and backup under its expected root.
- Reject a managed source or destination that is a symlink, escapes its root,
  crosses into an excluded path, or changes type between inspection and write.
- Read ordinary files without following descendant symlinks. Report an unsafe
  path as a blocker without printing sensitive target details.
- Recheck the exact write plan immediately before mutation. A changed plan
  invalidates the dry run.

## Report The Evidence Boundary

Separate observed files, command output, user-provided facts, and unknowns.
State what was excluded and which command established drift. Do not infer
runtime enablement, trust, authentication, or cross-host equality from file
presence or a zero-drift audit.
