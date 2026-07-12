# Source Notes

Checked: 2026-07-12.

Classification: hybrid. The initial skill is local-origin, while the current
design deliberately internalizes selected Superpowers methods and official
Codex product contracts. Available Git history does not prove that the initial
text was copied from an upstream skill. Local authorization, user-change
protection, host boundaries, and specialist workflow ownership take precedence.

## Superpowers v6.1.1

- Release: [v6.1.1](https://github.com/obra/superpowers/releases/tag/v6.1.1)
- Annotated tag object: `c984ea2e7aeffdcc865784fd6c5e3ab75da0209a`
- Peeled commit: `d884ae04edebef577e82ff7c4e143debd0bbec99`
- License: MIT, Copyright (c) 2025 Jesse Vincent.
- License blob: `abf0390320aa14406af7a520b9b0739fdda9bf08`
- License SHA-256:
  `a37e0e9697144819e1d965176ac4ae5bc3fa02d11e7812036bbcadf6dafe2400`

Pinned design sources:

| Source | Git blob | SHA-256 | Bytes |
| --- | --- | --- | ---: |
| [`dispatching-parallel-agents/SKILL.md`](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/dispatching-parallel-agents/SKILL.md) | `75e7e22cef2e7adc0963e74457cf2664514dee33` | `f0df13f584049059cc5619f90061405b89dcc6e28ab3f2a8517d27d99c7a46a6` | 6,644 |
| [`subagent-driven-development/SKILL.md`](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/subagent-driven-development/SKILL.md) | `d8ca081570c1ae7cc86e15f125c2b6063000f755` | `41ab239a6ad1c487cd839fdac972a8c9cf0f5e90efa59a63f963767864f0df4c` | 21,647 |
| [`implementer-prompt.md`](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/subagent-driven-development/implementer-prompt.md) | `218fcfeb57e62626a22851cef77807e65db874bf` | `49018b28dc11bc9f3d13a28959bb10ae1a96eabc5d8f19f4079d901f9ff2bf64` | 5,522 |
| [`task-reviewer-prompt.md`](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/subagent-driven-development/task-reviewer-prompt.md) | `588a40227a79bf7ef97fb5b93f10f0f8f5f867b4` | `2eb9d54373420de25bc0bd00635d3a3123a6c0eb30c881168e6f3348e2387331` | 7,919 |

## Official Codex Evidence

- [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
  documents built-in and custom agents, standalone files under
  `~/.codex/agents/` or `.codex/agents/`, required role fields, inherited
  configuration, and optional `model`, `model_reasoning_effort`, and
  `sandbox_mode` settings. It also states that unpinned agents may be selected
  dynamically for task cost and depth, and that live parent runtime overrides
  are reapplied when a child is spawned even when a custom file declares
  different defaults.
- [Configuration Reference](https://learn.chatgpt.com/docs/config-file/config-reference)
  documents `agents.<name>.config_file` and supported reasoning configuration.
- Local check: `codex-cli 0.144.1` reported `multi_agent` as stable. The current
  model catalog contained `gpt-5.6-terra` and `gpt-5.6-sol`; both supported the
  reasoning levels selected by the local `monitor` and `reviewer` profiles on
  the check date.

Official pages are current documentation rather than commit-pinned source. Recheck
them and the local model catalog when auditing model names, reasoning levels, or
custom-agent schema.

## Local History

- Initial local commit: `6574bce5f5ede8fb4566d0451ddcf613f7fdf8a5`
- Initial `SKILL.md` blob: `96b5e0c180bbed8f39605013f2ae123688aee5c4`
- Initial `agents/openai.yaml` blob: `5fef7e34a15cf6ebe9a389e16264737084455ed7`
- Monitoring expansion commit:
  `4ad4abb3f08ef347e299ea8ddf9d19cb7f3a4835`

The monitoring expansion established useful local anomaly and observer
boundaries but also placed the full protocol in the main skill. The current
revision retains the useful contract in a progressive-disclosure reference.

## Adopted

- Split only independent problem domains and avoid parallel shared-state work.
- Give each worker a focused, self-contained objective, scope, constraints,
  stop condition, and evidence-bearing report.
- Use raw artifacts and minimal context for independent review.
- Require changed paths, verification evidence, concerns, and a recommended
  outcome from workers.
- Keep integration and authoritative coordination decisions with the
  coordinator.
- Use current Codex custom-agent profiles for roles with stable model,
  reasoning, and sandbox needs.

## Adapted

- Replace upstream agent-launch syntax with Codex delegation contracts and the
  smallest sufficient `fork_turns`.
- Expand exclusive files into the complete mutation surface, including
  generated artifacts and indirect side effects.
- Separate worker execution status and `recommended_outcome` from coordinator
  states such as `pass` and `no-go`.
- Use custom `monitor` and `reviewer` profiles without treating the parent
  agent's current model or reasoning effort as a baseline.
- Keep the portable parent config model- and effort-neutral while making the
  non-recursive `agents.max_depth = 1` default explicit.
- Use scoped worker verification, coordinator intake, and
  `personal-risk-verification` as separate evidence layers.
- Keep active-monitoring detail in a reference loaded only after current-stage
  authorization.

## Rejected

- Claude-specific `Task` syntax and assumptions about one-response parallelism.
- Mandatory new implementer, double review, full suite, commit, worktree, or
  whole-plan continuation for every delegated task.
- Majority voting as a substitute for discriminating evidence.
- Automatic commits, next-stage launch, model escalation, or external actions
  by workers.
- Fixed parent-agent model or reasoning assumptions.
- Prompt-only claims that a model or reasoning switch took effect.
- A custom profile for every possible worker type before its execution needs
  are stable.
- Persistent `.superpowers/sdd` ledgers and project files for ordinary one-shot
  delegation.

## Local Deviations

- The portable profile currently allowlists only the `monitor` and `reviewer`
  custom agents. Adding another profile requires a deliberate lifecycle and
  synchronization decision.
- Official Codex uses the `name` field as the agent identity and permits more
  `config.toml` keys. This profile additionally requires filename/name equality
  and accepts only a reviewed portable subset of fields and TOML syntax so
  `verify` cannot silently approve unreviewed configuration.
- `monitor` is read-only and does not write a durable record. A separately
  authorized supervisor owns any persistent monitoring record.
- If the configured monitoring profile cannot be enforced, the default fallback
  is no watcher rather than silently inheriting an unknown parent profile.
- Explorer, worker, validator, and diagnostic model choices remain
  task-dependent.
- Persistent worktree and line state belongs to
  `personal-multiline-coordination`; final completion belongs to
  `personal-risk-verification`.
