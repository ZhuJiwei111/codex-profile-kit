# Source Notes

## Local Artifact

- Skill: `personal-code-simplifier`
- Review date: 2026-07-11
- Local purpose: perform explicitly requested or workflow-scheduled bounded
  code simplification while preserving observable behavior and protected user
  changes.

## Pinned Official Source

- Project: [Anthropic official Claude plugins](https://github.com/anthropics/claude-plugins-official)
- Checked `main` commit:
  [`6fbe3b01859cc0c4e84ba66028cffd91f2b02d93`](https://github.com/anthropics/claude-plugins-official/commit/6fbe3b01859cc0c4e84ba66028cffd91f2b02d93)
- Plugin subtree:
  [`plugins/code-simplifier`](https://github.com/anthropics/claude-plugins-official/tree/6fbe3b01859cc0c4e84ba66028cffd91f2b02d93/plugins/code-simplifier)
- Upstream artifact type: Claude Code plugin containing one agent, not a
  Codex `SKILL.md`
- Agent file:
  [`agents/code-simplifier.md`](https://github.com/anthropics/claude-plugins-official/blob/6fbe3b01859cc0c4e84ba66028cffd91f2b02d93/plugins/code-simplifier/agents/code-simplifier.md)
- Agent blob: `05e361b4ef1b688203251989707f8a924a9ed266`
- Agent content commit:
  [`ceb9b72b4c4c20ad39efce780edd0aabe80ebce3`](https://github.com/anthropics/claude-plugins-official/commit/ceb9b72b4c4c20ad39efce780edd0aabe80ebce3)
- Plugin manifest:
  [`.claude-plugin/plugin.json`](https://github.com/anthropics/claude-plugins-official/blob/6fbe3b01859cc0c4e84ba66028cffd91f2b02d93/plugins/code-simplifier/.claude-plugin/plugin.json)
- Manifest blob: `e8edbae4330809cc9202951db1c9d5f27c39ed76`
- Manifest version: `1.0.0`; this is not a repository tag or release
- License: [Apache License 2.0](https://github.com/anthropics/claude-plugins-official/blob/6fbe3b01859cc0c4e84ba66028cffd91f2b02d93/plugins/code-simplifier/LICENSE)
- License blob: `d645695673349e3947e8e5ae42332d0ac3164cd7`
- License addition commit:
  [`aecd4c852f10b466245f18383fa6aad8c0b10d57`](https://github.com/anthropics/claude-plugins-official/commit/aecd4c852f10b466245f18383fa6aad8c0b10d57)
- Upstream checked: 2026-07-11

The official plugin contains only its manifest, agent file, and license. It has
no Codex skill metadata, scripts, references, tests, or evals to inherit. The
pinned source is design evidence, not a runtime dependency.

## Adopted

- Preserve observable behavior and established contracts.
- Prefer clarity, explicit flow, consistency, and maintainability over fewer
  lines.
- Reduce unnecessary nesting, duplication, and cleverness.
- Follow established project conventions instead of applying generic style.
- Keep cleanup local and report only changes material to understanding.

## Rewritten For Local Codex

- Replaced the autonomous Claude agent with a conditional Codex workflow that
  requires an explicit request or authorized scoped handoff.
- Replaced `CLAUDE.md` assumptions with applicable `AGENTS.md`, repository
  instructions, and current code evidence.
- Narrowed “recently modified” to a user-selected or provenance-clear owned
  diff and protected pre-existing user hunks.
- Expanded behavior preservation to outputs, errors, side effects, ordering,
  APIs, configuration, serialization, observability, and relevant resource
  contracts.
- Added a fresh pre-change preserving baseline, same-check comparison, and
  final scoped diff review.
- Added public, dynamic, compatibility, reflection, and generated-ownership
  gates for renames, deduplication, comment removal, and dead-code removal.
- Routed review disposition, unexpected failures, final verification, Git
  readiness, and temporary helpers to their owning personal skills.

## Rejected Or Deliberately Omitted

- No `model: opus` or other Claude model binding.
- No automatic cleanup after every code-writing task.
- No Claude plugin manifest, agent registration, or invocation mechanism.
- No hard-coded JavaScript, TypeScript, React, or framework style preference.
- No expansion from a recently touched file to unrelated code.
- No use of elegance or line-count reduction as the success criterion.
- No dead-code conclusion from absent direct calls alone.
- No behavior change, dependency addition, configuration expansion, public API
  change, broad formatter run, commit, push, or external mutation hidden inside
  cleanup.

## Local Ownership Boundaries

- `personal-code-simplifier` owns the authorized cleanup scope, behavior
  contract, clarity transformations, and final cleanup diff review.
- `personal-test-first-changes` owns the preserving baseline and focused
  before/after evidence.
- `personal-review-response` owns review feedback disposition and local
  implementation authorization.
- `personal-evidence-debugging` owns unexplained failures.
- `personal-repo-intake` owns uncertain repository and generated-source facts.
- `personal-temporary-work` owns approved one-off helpers and codemods.
- `personal-risk-verification` owns final completion evidence.
- `personal-branch-finish` owns Git readiness and handoff.
