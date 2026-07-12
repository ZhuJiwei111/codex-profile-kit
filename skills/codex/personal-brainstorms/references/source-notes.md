# Source Notes

Checked: 2026-07-11.

This skill adapts selected design behaviors from upstream evidence while
preserving the local Codex authorization model, lightweight scope gate, and
specialist skill boundaries. It does not copy upstream scripts, assets, flow
diagrams, or substantial prose.

## Sources

| Source | Pin or version | License/status | Role |
| --- | --- | --- | --- |
| [Superpowers `brainstorming`](https://github.com/obra/superpowers/blob/v6.1.1/skills/brainstorming/SKILL.md) | Annotated tag object `c984ea2e7aeffdcc865784fd6c5e3ab75da0209a`; commit `d884ae04edebef577e82ff7c4e143debd0bbec99` | [MIT](https://github.com/obra/superpowers/blob/v6.1.1/LICENSE), Copyright (c) 2025 Jesse Vincent | Scope decomposition, component boundaries, inline spec review, goal-related nearby improvement, and just-in-time visual judgment |
| [Superpowers v6.1.1 release](https://github.com/obra/superpowers/releases/tag/v6.1.1) | Immutable release dated 2026-07-02 | Upstream release evidence | Fixed comparison baseline; do not imply that every adopted brainstorming behavior was introduced by this release |
| Local `skill-creator` | Current host copy checked 2026-07-11 | Built-in Codex skill | Progressive disclosure, trigger metadata, deterministic UI metadata, and forward-testing guidance |
| Local `AGENTS.md` | Accepted portable revision checked 2026-07-11 | Personal profile instructions | Global authorization, discussion signals, ask-first boundaries, language, and simple-task handling |
| Local `personal-grilling` | Current host copy plus user-approved composition design checked 2026-07-11 | Personal profile skill | Manual rigorous clarification, critical-question admission, answer lockability, and blocking decisions |

## Adopted

- Run a scope preflight before detailed questions and decompose multiple
  independently deliverable subsystems.
- Ask one blocking question at a time and prefer a recommendation when a real
  choice exists.
- For complex designs, define component responsibilities, interfaces,
  dependencies, data or control flow, failure behavior, and verification.
- Review the design inline for placeholders, contradictions, scope drift,
  ambiguity, weak boundaries, and acceptance gaps.
- Include only nearby structural improvements that directly support the goal.
- Use visual assistance only when seeing the relationship or layout is
  materially clearer than reading prose.

## Deliberately Rejected

- Mandatory brainstorming, a design approval cycle, or formal tasks for every
  simple project or configuration edit.
- Inventing 2-3 approaches when only one path is credible.
- Mandatory approval after every design section.
- Mandatory design files under `docs/superpowers/specs/` or automatic commits.
- Treating an upstream `writing-plans` skill as the only valid handoff.
- Copying or running the upstream Visual Companion server, HTML screen protocol,
  browser event state, or helper scripts.

## Local Deviations

- `AGENTS.md` owns recognition of discussion signals and global authorization;
  this skill owns the conditional design workflow after routing.
- A clear, simple, low-risk implementation request bypasses brainstorming.
- The original request supplies discussion, planning, or implementation
  authority; brainstorming does not create or revoke it.
- When both personal skills are explicitly invoked, brainstorming coordinates
  design while `personal-grilling` gates only critical questions and blocking
  decisions. They share one decision state rather than running two interviews.
- The reciprocal release and same-turn planning behavior remains owned by the
  separately revised `personal-grilling` contract.
- Ordinary planning uses the built-in plan; file-backed planning is routed to
  `personal-planning-with-files-zh` only when explicitly required.
- Native tables, Mermaid, or compact wireframes replace the external visual
  companion.

## Refresh Policy

When refreshing from upstream, pin the new tag or commit, compare behavior
rather than wording, preserve deliberate local deviations, and re-run simple,
decomposition, concern, and combined-skill forward probes before adoption.
