# Source Notes

Checked: 2026-07-12.

## Local Artifact

- Skill: `personal-code-documentation`
- Local purpose: explain existing code, create evidence-grounded architecture,
  API, onboarding, tutorial, reference, or walkthrough artifacts, and
  synchronize an existing stale documentation contract for a defined reader.
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

## Merged `sync_existing` Provenance

The retired `personal-docs-sync-light` workflow was upstream-derived from a
user-identified OpenAI Agents JS `docs-sync` source, with substantial local
narrowing and redesign. Its exact historical upstream commit is not established.
The fixed comparison and internalization baseline is:

- Repository: <https://github.com/openai/openai-agents-js>
- Fixed comparison commit: `901fb94c0fb9ffc8cb2d8275d99622475f77f401`
- Skill:
  <https://github.com/openai/openai-agents-js/blob/901fb94c0fb9ffc8cb2d8275d99622475f77f401/.agents/skills/docs-sync/SKILL.md>
- Coverage checklist:
  <https://github.com/openai/openai-agents-js/blob/901fb94c0fb9ffc8cb2d8275d99622475f77f401/.agents/skills/docs-sync/references/doc-coverage-checklist.md>
- License: MIT, Copyright (c) 2025 OpenAI:
  <https://github.com/openai/openai-agents-js/blob/901fb94c0fb9ffc8cb2d8275d99622475f77f401/LICENSE>

Reviewed portable tree identities retained for retirement and provenance
closure (`sha256-path-content-v1`):

- `36c32775022ea3590690ea533ed798f2732a9953f3bd12df4c0216341f58ea70`
- `d724aa2b0afdff7f4cb5f2a671a64328c9fcca1ec18011dde395ef0a0c54d9ea`
- `52089bce134700c1a4d891afeca4e282b39bcdf642ab177e5650bae6da6bb430`

The merged mode internalizes the bounded contract delta, path-plus-symbol or
setting evidence, doc-first and code-first passes, target-page reasoning, and
narrow snippet validation. It rejects repository-specific paths, tools,
language exclusions, comprehensive main-branch scans, automatic installation,
publication, or external mutation. Retain this attribution and license record
when distributing the substantially derived `sync_existing` material.

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

- `personal-code-documentation` owns codebase-derived explanations, new or
  substantially rewritten standalone documentation, and bounded stale-contract
  patches through `sync_existing`.
- `personal-project-output-explainer` owns comprehension of existing Codex or
  project outputs and decisions.
- `personal-writing-polish` owns expression-only revision after facts and
  evidence are locked.
- `personal-review-response` owns feedback disposition and authorization;
  `personal-evidence-debugging` owns unexpected failure investigation.
- `personal-brainstorms` owns unresolved consequential design, and
  `personal-temporary-work` owns one-off evidence helpers. Unclear repository
  facts stop at bounded inspection and the smallest decision-changing question.
- `personal-risk-verification` is the final completion gate after file changes,
  and `personal-branch-finish` owns later Git readiness.

```yaml
skill_admission:
  skill: personal-code-documentation
  acquisition_mode: created
  source_classification: hybrid
  provenance_status: partial
  admission_status: legacy-exception
  portability_disposition: internalized
  safety_status: passed
  safety_review: "static_pass: Static review found an instruction-and-reference-only skill; writes are limited to explicitly authorized documentation artifacts and no publication, credential, installation, or destructive surface is bundled."
  trigger_status: passed
  trigger_review: "static_pass: Explain, create, and sync_existing ownership was reviewed against output explanation, prose polishing, review response, debugging, and consequential design."
  validation_status: passed
  validation:
    - "static_pass: Pinned documentation sources, retained retirement tree identities, licenses, and the historical source gap reviewed on 2026-07-16."
    - "static_pass: Targeted personal-skill admission validator fixtures passed on 2026-07-16."
  update_owner: "maintainer of personal-code-documentation"
  update_rule: "No update is authorized; any content, source, trigger, executable, or metadata change requires a fresh re-admission before portable export."
  rollback_basis: "The pre-batch rollback source is exact codex-profile-kit revision 3791645f59c0eeec497755bd7301be78b44efbea and exact tree 074ebe5e1fe21df47535ea0a88a1e74bd357f5ae; the current compatibility-only allowed content is separately locked by the validator's reviewed sha256-path-content-v1 full-tree digest."
  unknowns_disposition: provenance-gap
  unknowns:
    - "The exact historical upstream commit that originally shaped the retired personal-docs-sync-light workflow is not established."
```
