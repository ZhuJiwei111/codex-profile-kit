# Source Notes

Checked: 2026-07-13.

This skill adapts selected design behaviors from upstream evidence while
preserving the local Codex authorization model, lightweight scope gate, and
specialist skill boundaries. It does not copy upstream scripts, assets, flow
diagrams, or substantial prose.

## Sources

| Source | Pin or version | License/status | Role |
| --- | --- | --- | --- |
| [Superpowers `brainstorming`](https://github.com/obra/superpowers/blob/v6.1.1/skills/brainstorming/SKILL.md) | Annotated tag object `c984ea2e7aeffdcc865784fd6c5e3ab75da0209a`; commit `d884ae04edebef577e82ff7c4e143debd0bbec99` | [MIT](https://github.com/obra/superpowers/blob/v6.1.1/LICENSE), Copyright (c) 2025 Jesse Vincent | Scope decomposition, component boundaries, inline spec review, goal-related nearby improvement, and just-in-time visual judgment |
| [Superpowers v6.1.1 release](https://github.com/obra/superpowers/releases/tag/v6.1.1) | Immutable release dated 2026-07-02 | Upstream release evidence | Fixed comparison baseline; do not imply that every adopted brainstorming behavior was introduced by this release |
| Local `skill-creator` snapshot | `codex-cli 0.144.1`; home-relative path `~/.codex/skills/.system/skill-creator/SKILL.md`; SHA-256 `da44c88f6b3845a8fa8c60792ec9a722110a55a9793c279757b48fefb11f819c`; checked 2026-07-12 | Built-in Codex skill; current-host evidence snapshot only | Progressive disclosure, trigger metadata, deterministic UI metadata, and forward-testing guidance |
| Local portable `AGENTS.md` | profile-kit revision `5ad41a7157352724ac51ad24f87949e3e23cc694`; repo path `rules/AGENTS.portable.md`; Git blob `e20fa56361bee15b1187bb377fb50170ae722ffa`; checked 2026-07-12 | Repository-exported personal profile instructions | Global authorization, discussion signals, ask-first boundaries, language, and simple-task handling |
| Local `personal-grilling` | Active path `~/.codex/skills/personal-grilling/SKILL.md`; profile-kit mirror `skills/codex/personal-grilling/SKILL.md`; strengthened local contract checked 2026-07-13 | Personal profile skill | Manual coverage-tree construction, sourced leaves, answer lockability, risk disposition, three closure passes, and explicit coverage confirmation |

The built-in `skill-creator` entry is a hash-addressed evidence snapshot of the
current host. It is not exported by profile-kit and is not a distributed
runtime dependency of this skill.

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
- When both personal skills are explicitly invoked, brainstorming is the sole
  design-synthesis owner. `personal-grilling` acts as an independent theme,
  coverage, and adversarial gate over one shared sourced ledger and returns no
  competing design or plan. It may reopen a material branch that brainstorming
  missed or closed without sufficient evidence.
- Brainstorming's solo lightweight-question filter does not restrict the paired
  grilling coverage model. Grilling still asks only unresolved material user
  decisions rather than turning every covered dimension into a question.
- The reciprocal release, explicit coverage confirmation, risk disposition,
  and same-scope authorization handoff remain owned by the separately revised
  `personal-grilling` contract.
- Ordinary planning uses the built-in plan; file-backed planning is routed to
  `personal-planning-with-files-zh` only when explicitly required.
- Native tables, Mermaid, or compact wireframes replace the external visual
  companion.

## Refresh Policy

When refreshing from upstream, pin the new tag or commit, compare behavior
rather than wording, preserve deliberate local deviations, and re-run simple,
decomposition, concern, and combined-skill forward probes before adoption.
