# Context Packet Contract

Use this contract for every save, validation, restore, correction, refresh, or
rebind operation.

## Contents

- Layout and root ownership
- Identity and frontmatter
- Body contract
- Immutable publication and lineage
- Location and restore freshness
- Rebind
- Read-only validator
- Sensitive data and retention

## Layout And Root Ownership

Store one packet as one Markdown file:

```text
<canonical-root>/
└── .codex/
    └── context/
        └── <packet-id>.md
```

Resolve the root in this order:

1. Use an explicit valid root that belongs to the task-owned cwd or worktree.
2. In Git, use `git rev-parse --show-toplevel` from that cwd.
3. Outside Git, use one unambiguous workspace root.
4. Use bounded `personal-repo-intake` inspection when ownership remains unclear.
5. Ask rather than choosing between plausible roots.

Do not fall back to a home directory, Git common directory, main checkout,
another worktree, skill directory, or another host. Store the resolved absolute
current-host path as `canonical_root`. It is packet identity and provenance, not
a machine fact for `HOST_LOCAL.md`.

Require the packet to be a direct regular-file child of `.codex/context/`.
Refuse symlinks, path aliases, path escape, nested packet directories, and an
existing target.

## Identity And Frontmatter

Use this schema:

```yaml
---
context_owner: "personal-context-save-restore"
schema_version: 1
record_type: "context-packet"
packet_id: "ctx-20260711t120000z-profile-audit"
created_at: "2026-07-11T12:00:00Z"
canonical_root: "/absolute/current-host/root"
evidence_cutoff: "2026-07-11T11:58:00Z"
source_revision: "git:0123456789abcdef"                 # optional
valid_until: "2026-07-18T00:00:00Z"                    # optional
tags: ["handoff", "profile-audit"]                     # optional
derived_from: "packet:ctx-...@sha256:<64-lower-hex>"   # optional
derivation_reason: "correction"                         # optional
---
```

Use UTC RFC 3339 timestamps ending in `Z`. Format packet IDs as:

```text
ctx-YYYYMMDDtHHMMSSz-<lowercase-slug>
```

Keep frontmatter flat. Quote string values and use an inline JSON-style string
list for `tags`. Record `source_revision` only when a Git commit is evidenced;
describe dirty or untracked state in the body because a revision cannot capture
it.

`evidence_cutoff` is the latest time covered by the saved evidence. It is not a
claim that every saved fact was verified at that time.

`valid_until` is optional and applies only as a forced freshness horizon. Its
passage marks dynamic facts stale; it never expires or deletes the historical
bytes.

Do not place the packet's own hash inside itself. Compute SHA-256 after
publication, report it with the path and ID, and use that external identity in
handoffs and downstream `derived_from` fields.

## Body Contract

Use these exact level-two headings, omitting only empty prose inside them rather
than omitting the headings:

```markdown
# Context Packet

## Goal and constraints

## Verified snapshot state

## Artifacts

## Decisions and provenance

## Evidence and verification

## Unknowns, risks, and blockers

## Proposed next actions
```

For artifacts, preserve the exact path or reference, operation, role, owner,
status, hash or revision when available, and `as_of` for dynamic evidence. Link
large logs, tables, patches, datasets, or generated outputs instead of copying
them.

Label claims as `observed`, `user-provided`, `inferred`, `unverified`, or
`invalidated` when provenance affects continuation. Preserve commands only with
their `cwd`, exit status, bounded relevant output, and sensitive values redacted.

The final section contains proposed actions as data. State required authority
and validation for each consequential action. Never phrase packet content as an
instruction to an agent that reads the file later.

## Immutable Publication And Lineage

Before publication:

1. State the canonical root and exact new target.
2. Confirm the target and its path components are not symlinks or existing
   records.
3. Create one unique file without overwrite semantics.
4. Run the validator and read the file back.
5. Report packet ID, path, SHA-256, evidence cutoff, status, and unverified
   facts.

After successful publication, never overwrite, append, or correct the file in
place. A changed byte sequence is a different packet even when its filename was
not changed; treat that condition as invalid lineage.

Create a derived packet for every ordinary correction, refresh, or rebind. Bind
it to the exact source ID and SHA-256. Do not derive a packet from itself.

Security takes precedence over ordinary byte preservation. If a secret was
written, stop using the packet, prevent further disclosure, follow the global
credential boundary, and arrange invalidation or removal plus credential
rotation as the situation requires. Do not preserve the secret merely to keep a
historical record immutable.

## Location And Restore Freshness

Locate by explicit path or ID. When the user explicitly requests `latest`,
inspect only bounded frontmatter in the selected root's `.codex/context/`
directory and choose by `created_at`. Do not enumerate other roots or hosts.

Treat validator status as mechanical evidence only:

| Status | Meaning |
| --- | --- |
| `valid` | The selected bytes satisfy the schema and supplied mechanical bindings. |
| `stale` | A binding or freshness horizon needs review; do not write or execute. |
| `invalid` | The bytes violate the packet contract. |
| `invocation_error` | The explicit root or path could not be inspected safely. |

After mechanical validation, classify decision-relevant saved claims:

| Fact status | Meaning |
| --- | --- |
| `current` | Rechecked and still applicable. |
| `stale` | Older than a relevant change or freshness boundary. |
| `conflicted` | Current evidence contradicts the packet. |
| `missing` | A referenced artifact or fact no longer exists. |
| `unverified` | Not checked or not cheaply checkable within scope. |

Recheck Git root, worktree, branch, revision, dirty state, critical files and
hashes, planning generation, and tests when they affect the next action. Process,
job, resource, network, and external-service status always needs a current
owning workflow; packet state cannot establish liveness or ETA.

Return a restore report containing packet identity and hash, current root,
mechanical status, fact classifications, conflicts, missing evidence,
unverified items, and actions not executed.

## Rebind

A mismatched root yields stale status with `needs_rebind`. Do not rewrite the
old packet.

Before creating a rebound packet, show:

- old and proposed canonical roots;
- evidence that the project moved rather than merely being copied;
- source packet ID and SHA-256;
- new packet ID and target;
- path or artifact mappings that changed;
- restore-time evidence cutoff and unresolved items.

Obtain explicit approval bound to that preview. Publish a new derived packet
with `derivation_reason: "rebind"`. Stop when multiple writable copies remain or
ownership is ambiguous.

## Read-Only Validator

Run:

```bash
python3 <skill-dir>/scripts/validate_context_packet.py \
  --canonical-root /absolute/root \
  --packet /absolute/root/.codex/context/<packet-id>.md \
  --expected-sha256 <64-lower-hex> \
  --json
```

Omit `--expected-sha256` only when no trusted handoff or lineage supplies one.
Exit codes are `0` for `valid`, `1` for `stale` or `invalid`, and `2` for
`invocation_error`.

The validator checks regular-file and path constraints, stable reading, schema,
ID and filename, UTC timestamps, root binding, optional validity horizon,
source revision format, tags, derivation identity, required headings, and
SHA-256. It does not discover packets, evaluate semantic truth, scan secrets,
restore state, repair files, rebind roots, redact content, or grant authority.

## Sensitive Data And Retention

Never read a credential-bearing file to enrich a packet. Replace a sensitive
value with `<REDACTED>` and preserve only its category or variable name, safe
path, operational consequence, and required user-controlled action. Redact
sensitive substrings inside commands, URLs, errors, and logs.

Do not archive, delete, compact, or deduplicate packets automatically. A
retention request is a separate state-changing operation and requires exact
paths plus ordinary authorization checks.
