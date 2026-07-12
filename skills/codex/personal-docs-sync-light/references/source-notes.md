# Source Notes

## Provenance Decision

- Skill: `personal-docs-sync-light`
- Classification: upstream-derived from a user-identified OpenAI source, with
  substantial local narrowing and redesign
- Checked: 2026-07-12
- Initial local commit: `6574bce5f5ede8fb4566d0451ddcf613f7fdf8a5`
- Initial local `SKILL.md` blob:
  `7dc050d7ad52801b875540347c5a5457cbf27356`
- Initial local `agents/openai.yaml` blob:
  `dd8e8ec1969b4ac8a574dfbc14aec8130764d987`

The user identified OpenAI Agents JS `docs-sync` as the source of the local
skill. The exact upstream commit used when the local skill was first created is
not established by the available metadata or Git history. The fixed revision
below is the current comparison and internalization baseline, not a claim about
the historical source revision.

## OpenAI Agents JS `docs-sync`

- Repository: <https://github.com/openai/openai-agents-js>
- Fixed comparison commit: `901fb94c0fb9ffc8cb2d8275d99622475f77f401`
- Skill:
  <https://github.com/openai/openai-agents-js/blob/901fb94c0fb9ffc8cb2d8275d99622475f77f401/.agents/skills/docs-sync/SKILL.md>
- Coverage checklist:
  <https://github.com/openai/openai-agents-js/blob/901fb94c0fb9ffc8cb2d8275d99622475f77f401/.agents/skills/docs-sync/references/doc-coverage-checklist.md>
- License: MIT, Copyright (c) 2025 OpenAI:
  <https://github.com/openai/openai-agents-js/blob/901fb94c0fb9ffc8cb2d8275d99622475f77f401/LICENSE>

The upstream workflow compares implementation and configuration with existing
documentation using a selected branch scope, path-plus-symbol evidence, a
doc-first pass, a code-first pass, target-page reasoning, an approval gate, and
snippet build validation. It also contains repository-specific paths, tools,
language exclusions, and full-main coverage behavior that are not portable to
this profile.

## Internalized Methods

- Use an explicit contract delta or a bounded current-branch diff instead of
  assuming a repository-wide scan.
- Capture path-plus-symbol, setting, command, or schema-key evidence without
  copying large source blocks.
- Combine a doc-first pass over likely owning pages with a code-first mapping
  from the identified user-facing surface.
- Classify coverage as current, stale, missing a small fact, or outside the
  light workflow.
- Choose an existing target page from reader intent, feature ownership,
  information architecture, and duplication risk.
- Distinguish a read-only coverage report from an already authorized bounded
  documentation edit.
- Verify identifiers, links, examples, and snippets with the repository's
  narrow existing checks when available and authorized.

## Local Narrowing And Redesign

- Trigger only after a CLI, API, configuration, installation, or workflow
  contract change has been identified; do not automatically audit all docs.
- Keep the full-main inventory behavior outside this skill. Even in branch-diff
  mode, inspect only the affected user-facing surfaces.
- Preserve documentation as a possible canonical specification instead of
  assuming implementation always overrides it.
- Protect generated, historical, versioned, translated, or frozen material
  according to the target repository's own ownership rules.
- Patch only the smallest existing factual surface. Route new or substantially
  rewritten artifacts to `personal-code-documentation`.
- Defer final completion judgment to `personal-risk-verification` and preserve
  the local authorization, environment, and Git boundaries.

## Deliberately Rejected

- No hard-coded `docs/src/content/docs` or `examples/docs` ownership.
- No English-only rule or fixed translated-directory exclusions.
- No `$openai-knowledge`, DeepWiki, or other project-specific MCP dependency.
- No fixed `pnpm -F docs-code build-check` or assumed package-manager command.
- No comprehensive main-branch documentation sweep under the light trigger.
- No mandatory fixed report template when the user already authorized a clear
  local documentation patch.
- No automatic branch switching, new worktree, dependency installation,
  publication, or external state change.

## License And Distribution

The fixed upstream source is MIT licensed. This local workflow paraphrases and
adapts its methods and does not depend on the upstream repository at runtime.
Retain the upstream attribution and license record when distributing material
substantially derived from it. The profile kit's own publication terms still
require an owner-approved license.

## Local Ownership Boundaries

- `personal-docs-sync-light` owns minimal factual synchronization of existing
  docs for an identified stable contract change.
- `personal-code-documentation` owns new or substantially rewritten standalone
  documentation.
- `personal-evidence-debugging` owns unexplained mismatches and failed checks.
- `personal-project-output-explainer` owns project-output comprehension.
- `personal-writing-polish` owns explicitly requested expression changes.
- `personal-risk-verification` owns final completion evidence.
