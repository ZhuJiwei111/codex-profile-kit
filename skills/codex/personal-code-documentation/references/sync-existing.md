# Sync Existing Documentation

Use this reference only for `sync_existing`: an identified stable contract
change has made existing supported documentation stale. It is not permission
for a broad documentation audit or a new documentation system.

## Lock The Contract Delta

Keep this record implicit for one obvious replacement and explicit otherwise:

```yaml
contract_source:
contract_delta:
  before:
  after:
target_version_and_audience:
docs_impact: required | none | unclear
stale_locations: []
replacement_facts: []
generated_owner:
verification: []
```

Use `required` only when an existing supported page is now false, misleading,
or missing a small fact needed to use the changed contract. Use `none` for an
internal refactor with no documented surface. Use `unclear` when the intended
behavior, source of truth, canonical page, generated owner, or replacement fact
is unstable; stop rather than rewriting a specification to match an accidental
implementation.

Prefer current verified CLI help or parser behavior, API schema or types,
configuration schema and defaults, approved installation requirements, a
locked workflow contract, or an accepted implemented review item. Run this mode
only after the relevant implementation or decision is stable enough to state.

## Bound Coverage

Start from the known change, not from every document:

1. Select the explicit contract delta, changed path and symbol, setting,
   command, schema key, or bounded branch diff.
2. Run a doc-first pass over the pages a reader would reasonably consult.
   Search old and new literals, nearby semantic anchors, direct links, and
   examples.
3. Run a code-first pass from each identified user-facing surface to the best
   existing page and section.
4. Classify each surface as `current`, `stale`, `missing-small-fact`, or
   `outside-sync-existing`.
5. Expand only when evidence shows another supported page restates the same
   contract. Record deliberately excluded historical or versioned pages.

For multiple surfaces, keep a compact record:

```yaml
surface:
contract_evidence: path + symbol | setting | command | schema key
before:
after:
candidate_pages: []
coverage: current | stale | missing-small-fact | outside-sync-existing
target_page_and_section:
target_reason:
validation: []
```

Prefer the current canonical reference, then the existing task-oriented page,
directly affected example or runbook, and finally a small addition to an
existing page. A new architecture guide, API manual, explanation, onboarding
tutorial, migration system, or navigation redesign is outside this mode.

## Patch And Verify

- Preserve repository terminology, structure, and established style.
- Change only the stale literal, link, example, snippet, prerequisite, default,
  cross-reference, or small paragraph required by the contract delta.
- Update a generated source and use its existing authorized generator; never
  hand-edit an output that will be overwritten.
- Preserve accurate historical, release, frozen, translated, and versioned
  material.
- Never copy credentials, authenticated URLs, or private values into docs.

After the last edit:

1. read the changed section in context and inspect the scoped diff;
2. search stale literals and semantic anchors, classifying legitimate old
   occurrences rather than replacing them blindly;
3. check affected links, anchors, paths, examples, identifiers, and snippets;
4. use the repository's existing narrow parser, schema, `--help`, docs,
   snippet, type, or dry-run check when available and authorized;
5. run `git diff --check` in a Git-backed repository; and
6. report exact checks, exit status, skipped checks, and remaining gaps.

Do not install dependencies, contact external services, launch a check expected
to exceed 10 minutes, publish, stage, commit, or change product behavior merely
to complete documentation synchronization. Unexpected mismatches or failed
checks return to `personal-evidence-debugging`; task-level completion remains
with `personal-risk-verification`.
