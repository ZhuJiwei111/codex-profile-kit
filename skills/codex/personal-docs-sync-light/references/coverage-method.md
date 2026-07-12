# Bounded Coverage Method

Read this reference only when an identified contract delta affects multiple
user-facing surfaces, exact-literal search is insufficient, or the correct
existing documentation page is unclear. This is not permission for a full
documentation audit.

## Select The Evidence Scope

Use the smallest scope that can establish the documentation impact:

1. Prefer the user's explicit contract, implementation, file, symbol, setting,
   or accepted change.
2. On a feature branch, identify the repository's evidenced default branch and
   inspect only the relevant diff or changed symbols. Do not switch branches or
   disturb local work merely to collect evidence.
3. On the default branch or in an uncommitted working tree, use the explicit
   changed files and symbols rather than inventorying every public feature.
4. If the base branch, contract source, or relevant change set is ambiguous,
   use `personal-repo-intake` or stop for clarification.

For each surface, keep a compact record:

```yaml
surface:
contract_evidence: path + symbol | setting | command
before:
after:
candidate_pages: []
coverage: current | stale | missing-small-fact | outside-light-scope
target_page_and_section:
target_reason:
validation:
```

Focus on user-visible exports, commands, configuration, environment variables,
defaults, installation requirements, runtime behavior, deprecations, removals,
and supported workflow changes. Ignore internal refactors that do not alter a
documented contract.

## Doc-First Pass

Inspect only the pages a reader would reasonably consult for the affected
contract:

- locate exact before and after literals;
- inspect the owning section and nearby semantic descriptions;
- follow direct cross-links and examples;
- note stale defaults, removed names, missing opt-in behavior, and conflicting
  versions;
- preserve historical or frozen pages that remain accurate for their scope.

Record a page as checked even when no change is required, with a short reason.
This prevents an exact-literal miss from being mistaken for complete coverage.

## Code-First Pass

Map each identified user-facing surface back to documentation:

- use path plus symbol, setting, command, or schema key as evidence;
- include behavior-critical defaults, ranges, and required versus optional
  semantics;
- find the closest existing page based on reader task, feature ownership, and
  repository conventions;
- prefer updating an existing canonical page over duplicating the contract;
- classify a missing large topic or information-architecture problem as
  outside the light workflow.

The code-first pass is not a general public-API inventory. Its boundary is the
already identified contract delta or bounded branch diff.

## Choose The Target Page

Select a target only when it is supported by the existing documentation
structure. Prefer, in order:

1. the current canonical reference for that command, API, or setting;
2. the existing task-oriented page where a reader needs the fact;
3. a directly affected example or runbook;
4. a small addition to an existing page when no exact section exists.

Do not create a new architecture guide, API manual, onboarding tutorial,
migration system, or navigation redesign under this skill. Route those outputs
to `personal-code-documentation` or `personal-brainstorms`.

## Validate Coverage And Snippets

- Re-run literal and semantic-anchor searches after editing.
- Verify paths, links, anchors, commands, defaults, identifiers, and signatures.
- For code snippets, compare them with the authoritative source and use an
  existing narrow snippet or docs check when available and authorized.
- Do not assume a project-specific package manager, docs directory, language
  policy, MCP tool, or build command.
- Report checked pages, changed pages, excluded pages, command exit status, and
  any snippet or generated-doc check that was not run.
