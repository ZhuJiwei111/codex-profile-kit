# Skill Provenance Contract

Use this contract for personal skills and externally acquired candidates. It
records why the skill exists and what evidence shaped it; it is not a runtime
dependency or permission to copy upstream content.

## Canonical Classification

Use one `source_classification`:

- `local-origin`: the workflow primarily comes from personal work experience
  or locally observed recurring needs;
- `upstream-derived`: an external skill, repository, paper, or official source
  supplies the primary workflow;
- `hybrid`: local experience defines the problem or boundaries and external
  sources materially shape the method; or
- `unresolved`: available evidence cannot support one of the other labels.

Report `provenance_status` separately as `complete`, `partial`, `missing`, or
`conflicting`. A plausible classification does not make its evidence complete.

## Minimum Record

Keep the record in `references/source-notes.md` for a personal skill and in the
reviewed third-party lock for a portable vendor. Include the applicable fields:

```yaml
skill:
source_classification:
provenance_status:
checked_at:
primary_sources: []
local_motivation:
adopted: []
rejected: []
local_deviations: []
runtime_dependency:
derivation:
update_owner:
update_rule:
provenance_gaps: []
```

The Markdown may use natural headings instead of literal YAML, but it must keep
these facts distinguishable. Existing notes that predate this contract may be
reported as legacy and migrated when that skill is materially updated; do not
rewrite every skill merely to normalize formatting.

## Evidence By Source Type

- **Versioned repository:** record repository/path, immutable tag or commit,
  license/status, checked date, and the relevant tree or blob when practical.
- **Live official documentation:** record the direct URL and checked date, and
  label it live or unpinned. Do not invent a commit.
- **Built-in local capability:** record Codex version, a home-relative path,
  content hash, and checked date. State that it is host evidence and is not
  exported or bundled.
- **Personal experience:** record the recurring problem, concrete motivation,
  observed failure or friction, and user-locked design decisions. Do not invent
  an upstream author, license, or version.
- **Local repository evidence:** record repository-relative paths, revision,
  Git tree/blob or content digest, and whether it proves source history or only
  the current snapshot.

## Derivation And Ownership

Use `derivation` such as `original`, `verbatim`, `adapted`, `conceptual`, or
`unknown`. Record what was adopted, deliberately rejected, and changed locally.

- A vendor snapshot keeps upstream semantics and has no unrecorded local
  semantic patch.
- An internalized skill transfers future semantic maintenance to the local
  profile and preserves the upstream relationship as design evidence.
- A source note does not make copied content license-compatible; retain license
  evidence and comply with its terms.
- Upstream material is evidence, not authority over local authorization,
  security, host, or collaboration rules.

## Fail-Closed Rules

- Never present mutable `main`, a search result, popularity, or a local copy as
  an immutable upstream revision.
- Never put secrets, authenticated URLs, raw transcripts, private values, or
  current-host absolute paths in portable provenance.
- If source, license, derivation, or local-modification evidence conflicts,
  record `conflicting` and defer portable adoption.
- `partial` is acceptable for a documented pre-contract legacy exception only
  when exact existing bytes are locked and updates are blocked pending review.
- A new vendor or internalized portable skill requires complete provenance.

## Refresh Triggers

Recheck provenance when the upstream revision changes, a vendor gains local
patches, a skill is renamed or internalized, its license/source changes, or a
Codex update changes the system authoring, installation, discovery, or metadata
contract. Do not refresh every source on every ordinary invocation.
