# Source Notes

Checked: 2026-07-12.

## Local Artifact

- Skill: `personal-code-documentation`
- Local purpose: explain existing code and create evidence-grounded
  architecture, API, onboarding, tutorial, reference, or walkthrough artifacts
  for a defined reader.
- Lifecycle disposition: renamed from `code-documentation` with no
  compatibility entry.
- A current-host recovery copy was verified during the rename. Recovery paths
  are host-local and intentionally excluded from the portable source record.
- Pre-rename `SKILL.md` SHA-256:
  `32f26a71741cffc621d8e9c9e235b819ed5863a310a03d429716ad5bfdfb0860`

## Local History And Baseline

- Initial profile-kit commit:
  `6574bce5f5ede8fb4566d0451ddcf613f7fdf8a5`
- Initial `SKILL.md` blob:
  `913763b9a6f567c75206bb9997323a567b73682c`
- The pre-rewrite recovery copy retained two previously approved route-name
  corrections that replaced `docs-sync` with
  `personal-docs-sync-light` and `code-simplifier` with
  `personal-code-simplifier`.

The pre-rewrite skill contained one 76-line `SKILL.md`, no
`agents/openai.yaml`, no references, and no scripts. Its three-mode direction
was useful, but the metadata overlapped stale-doc synchronization, existing
output explanation, prose-only polishing, diagnosis, and review. Its review
routes also named two skills that no longer exist.

The old skill passed the basic `quick_validate.py` check. That validator did
not cover the missing UI metadata, stale route names, trigger overlap, evidence
strength, or mode-specific artifact behavior.

## Pinned Upstream Source

- Project: [wshobson/agents](https://github.com/wshobson/agents)
- Checked `main` commit:
  [`2de74ac1c8f6669821dcef13153332c3168033c1`](https://github.com/wshobson/agents/commit/2de74ac1c8f6669821dcef13153332c3168033c1)
- Plugin subtree:
  [`plugins/code-documentation`](https://github.com/wshobson/agents/tree/2de74ac1c8f6669821dcef13153332c3168033c1/plugins/code-documentation)
- `.codex-plugin` manifest:
  [`plugin.json`](https://github.com/wshobson/agents/blob/2de74ac1c8f6669821dcef13153332c3168033c1/plugins/code-documentation/.codex-plugin/plugin.json)
- Manifest blob: `8d2b3e2596b9f431ec2651b4db3f7889c50f9712`
- Manifest version: `1.2.1`; this is plugin metadata, not a repository tag.
- License: [MIT](https://github.com/wshobson/agents/blob/2de74ac1c8f6669821dcef13153332c3168033c1/LICENSE), Copyright (c) 2024 Seth
  Hobson.
- Upstream checked: 2026-07-12.

Relevant fixed artifacts:

- [`docs-architect.md`](https://github.com/wshobson/agents/blob/2de74ac1c8f6669821dcef13153332c3168033c1/plugins/code-documentation/agents/docs-architect.md),
  blob `f00cb829cdc3f3121adc28f10622ade6ff4c3cf1`.
- [`tutorial-engineer.md`](https://github.com/wshobson/agents/blob/2de74ac1c8f6669821dcef13153332c3168033c1/plugins/code-documentation/agents/tutorial-engineer.md),
  blob `a7d47c7724fa2730cb51ad353506297f8622c6f0`.
- [`code-explain.md`](https://github.com/wshobson/agents/blob/2de74ac1c8f6669821dcef13153332c3168033c1/plugins/code-documentation/commands/code-explain.md),
  blob `42f2096be16566b18359d3ebdddb47683e860e35`.
- [`doc-generate.md`](https://github.com/wshobson/agents/blob/2de74ac1c8f6669821dcef13153332c3168033c1/plugins/code-documentation/commands/doc-generate.md),
  blob `4095dc8274fd606c26468b2915ed04951e868548`.
- [`code-reviewer.md`](https://github.com/wshobson/agents/blob/2de74ac1c8f6669821dcef13153332c3168033c1/plugins/code-documentation/agents/code-reviewer.md),
  blob `7972beb0d273d258c463ab30a78601701f76fb5a`,
  inspected only to define a rejected review boundary.

The upstream Codex manifest points to `skills: "./skills/"`, but the pinned
plugin tree does not contain that directory. Upstream adapter tooling derives
Codex artifacts from Claude-oriented agents and commands. The pinned source is
therefore design evidence, not a runtime dependency or directly installed
replacement.

## Adopted

- Separate discovery, information structure, and writing.
- Establish the audience, task, and artifact before choosing depth or sections.
- Use progressive disclosure from system purpose to representative flow and
  then to implementation detail.
- Offer different reading paths for callers, maintainers, operators, and new
  contributors when those roles materially differ.
- Define tutorial outcomes, prerequisites, dependency-ordered steps, hands-on
  examples, checkpoints, common errors, and recovery.
- Explain code from a mental model through control or data flow to selective
  local detail.
- Use diagrams and structured documentation types only when the relationship
  or reader task warrants them.

The adopted methods are paraphrased and integrated with local Codex rules; no
upstream command template or substantial block is copied into the skill.

## Rewritten For Local Codex

- Retained three explicit modes while making `explain` conversational and
  read-only by default.
- Added mode-specific audience and artifact defaults plus a compact contract
  for substantial persistent outputs.
- Added source, execution, authoritative-external, and inference evidence
  classes with claim-strength limits.
- Distinguished precise conversational line links from stable identifiers in
  long-lived documentation.
- Made visuals conditional and required every relationship to remain auditable
  in evidence and prose.
- Replaced Claude agent, command, model, and plugin invocation assumptions with
  one conditional Codex skill and `agents/openai.yaml` metadata.
- Integrated repository instructions, protected user changes, final local
  verification, and explicit Git and external-state boundaries.

## Rejected Or Deliberately Omitted

- No `model: sonnet`, `model: opus`, `Use PROACTIVELY`, `$ARGUMENTS`, slash
  command, or Claude marketplace behavior.
- No fixed 10-100-page target, mandatory universal outline, or default
  generation of every documentation type.
- No copied generic Python analyzers, placeholder templates, automatic OpenAPI
  generation, CI/CD configuration, hosted documentation site, deployment, or
  publication.
- No design rationale, history, production state, performance, scale, security,
  or reliability claim inferred from source structure alone.
- No code review, vulnerability scanning, static-analysis orchestration,
  defect disposition, implementation, or behavior-changing cleanup hidden in
  documentation work.
- No intentional tutorial failure or project mutation without exact authority.
- No compatibility alias for the retired `code-documentation` identity.

## Local Ownership Boundaries

- `personal-code-documentation` owns codebase-derived explanations and new or
  substantially rewritten standalone documentation.
- `personal-docs-sync-light` owns bounded stale-contract patches to existing
  documentation.
- `personal-project-output-explainer` owns comprehension of existing Codex or
  project outputs and decisions.
- `personal-writing-polish` owns expression-only revision after facts and
  evidence are locked.
- `personal-review-response` owns feedback disposition and authorization;
  `personal-evidence-debugging` owns unexpected failure investigation.
- `personal-brainstorms` owns unresolved consequential design;
  `personal-repo-intake` owns unclear repository facts; and
  `personal-temporary-work` owns one-off evidence helpers.
- `personal-risk-verification` is the final completion gate after file changes,
  and `personal-branch-finish` owns later Git readiness.
