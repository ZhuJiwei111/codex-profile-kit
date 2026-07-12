---
name: personal-docs-sync-light
description: Use only to update existing docs made stale by an identified CLI, API, config, installation, or workflow contract change.
---

# Personal Docs Sync Light

Synchronize existing documentation only from a stable, evidenced contract
delta. Own the smallest factual patch and its local documentation checks; do
not create a new documentation system or claim final task completion.

## Lock The Contract Delta

Keep a compact record when the change is not a single obvious literal:

```yaml
contract_source:
contract_delta:
  before:
  after:
target_version_and_audience:
docs_impact: required | none | unclear
stale_locations:
replacement_facts:
generated_owner:
verification:
```

- Use `required` when an existing supported document is now false,
  misleading, or missing a small fact required to use the changed contract.
- Use `none` for internal refactors, formatting, test-only changes, and other
  changes with no CLI, API, configuration, installation, or workflow impact.
- Use `unclear` when the intended behavior, source of truth, target version,
  canonical document, generated owner, or replacement facts are not stable.
  Stop instead of guessing.

For one clear flag, field, path, or command replacement, keep the record
implicit. Do not turn a small documentation correction into a planning ritual.

Establish the authoritative contract before editing. Prefer current verified
CLI help or parser behavior, API schema or types, configuration schema and
defaults, approved installation requirements, a locked workflow contract, or
an accepted and implemented review item. If documentation is the canonical
specification and code may be wrong, do not silently rewrite the specification
to match an accidental implementation.

Run this workflow only after the relevant implementation or decision is stable
enough to document. Route an unresolved code-versus-docs mismatch to
`personal-evidence-debugging`, and route a consequential contract decision to
its design or implementation owner.

## Locate The Owned Documentation Surface

Start from the known contract delta rather than scanning every document:

1. Select the smallest evidence scope. Prefer the explicit contract delta. If
   the change is isolated on a branch, use its bounded diff against the
   repository's evidenced default branch. Do not turn a local delta into a
   comprehensive main-branch documentation audit.
2. Capture each affected user-facing surface as a short path-plus-symbol or
   path-plus-setting record. Include the changed default, behavior, or removal
   when it affects documentation accuracy; avoid large code dumps.
3. Run a bounded doc-first pass over the pages most likely to own the contract.
   Search for old and new literals plus nearby semantic anchors, synonyms, and
   direct cross-references.
4. Run a bounded code-first pass from the identified CLI, API, config,
   installation, or workflow surface back to the best existing page and
   section. Classify coverage as current, stale, missing-small-fact, or outside
   this skill.
5. Choose the target page based on reader intent, existing information
   architecture, package or feature ownership, and duplication risk. Prefer an
   existing canonical page. Route a genuinely new standalone artifact or
   structural redesign to `personal-code-documentation` or
   `personal-brainstorms`.
6. Expand only when evidence shows another supported page restates the same
   contract. Record intentionally excluded pages and why.

For multiple surfaces or ambiguous page ownership, read
[coverage method](references/coverage-method.md). Skip that reference for a
single obvious literal replacement.

Identify ownership before editing:

- For generated documentation, update the canonical input and use the existing
  generator when that run is authorized and proportionate. Do not hand-edit an
  output that will be overwritten.
- Preserve historical release notes, migration records, frozen examples, and
  older version documentation when they accurately describe their own version.
- Update only the supported versions and audiences affected by the contract
  delta.
- Use `personal-repo-intake` when the canonical source, generated owner, edit
  surface, or documentation verification command is genuinely unclear.

## Patch The Smallest Factual Surface

- Preserve repository terminology, document structure, and established style.
- Replace the stale fact and the directly affected example, prerequisite, or
  cross-reference.
- Add a small missing paragraph or example inside an existing canonical
  document only when it is necessary to represent the changed contract.
- Update multiple current locations only when they genuinely restate the same
  contract; do not redesign the documentation hierarchy as incidental cleanup.
- Keep commands, defaults, version constraints, paths, and required versus
  optional behavior exact.
- Use safe placeholders such as `<REDACTED>` for credentials and never copy
  tokens, authenticated URLs, or private values into documentation.

Do not use this light workflow to create or substantially rewrite an
architecture guide, API manual, onboarding tutorial, documentation site,
changelog, release note, or migration guide. Do not add speculative behavior,
rewrite prose unrelated to the stale fact, or turn factual synchronization into
a broad style pass.

## Verify The Documentation Patch

After the last relevant documentation edit:

1. Read the changed section in context and inspect the scoped diff.
2. Search for stale before-literals and semantic anchors. Classify legitimate
   historical or versioned occurrences instead of replacing them blindly.
3. Check local links, anchors, referenced paths, filenames, and directly
   affected examples. For snippets, confirm copied identifiers and signatures
   against their source and run the repository's narrow snippet or docs check
   when it already exists and is authorized.
4. Use the narrowest safe contract check when available: parser or schema
   validation, `--help`, import or type checks, an existing docs check, snippet
   validation, or a non-mutating dry run. Do not invent a project-specific
   build command.
5. Run `git diff --check` in a Git-backed repository.
6. Report exact checks, exit results, skipped commands, and remaining evidence
   gaps.

Do not install software, download dependencies, contact external services, run
destructive commands, or launch a check expected to exceed 10 minutes merely
to validate documentation. Request the applicable authority or report the
unverified item.

These checks validate the documentation patch only. Hand the final repository
state to `personal-risk-verification` after this skill; do not reuse earlier
implementation evidence as proof that the later docs edit is complete.

## Collaboration And Boundaries

- A request to audit or propose documentation coverage remains read-only and
  reports evidence, target pages, and proposed edits. A request to update the
  identified stale documentation authorizes the bounded local edit; do not ask
  again unless target ownership, scope, or replacement facts remain material
  decisions.

- `personal-test-first-changes` or the implementation owner supplies stable
  behavior and generator-contract evidence; docs-only synchronization does not
  manufacture RED.
- `personal-review-response` first decides whether review feedback is accepted
  and locally authorized.
- `personal-evidence-debugging` owns unexplained command failures, generator
  failures, and code-versus-docs mismatches.
- `personal-repo-intake` owns genuinely unclear repository and documentation
  ownership facts.
- `personal-brainstorms` owns new information architecture, large documentation
  systems, and unresolved product or contract choices.
- `personal-code-documentation` owns new or substantially rewritten standalone API,
  architecture, onboarding, tutorial, and walkthrough artifacts.
- `personal-project-output-explainer` may decode existing documentation-sync
  evidence or a decision only when the user explicitly expresses a
  comprehension need. It does not own ordinary status, summary, report,
  completion, or next-step output, and it does not maintain canonical
  repository docs.
- `personal-writing-polish` changes expression only after facts are locked and
  only when explicitly requested.
- `personal-temporary-work` owns any approved one-off structured evidence scan;
  this skill still owns the factual docs patch.
- `personal-risk-verification` is the single final completion gate, and
  `personal-branch-finish` handles later Git readiness.

An internal behavior-preserving cleanup by `personal-code-simplifier` does not
automatically trigger this skill. This workflow also does not authorize
staging, commit, push, publication, reviewer replies, or external state changes.

## Source Provenance

See [source notes](references/source-notes.md) for the user-identified OpenAI
upstream origin, fixed comparison revision, local narrowing, license, and
ownership boundaries.
