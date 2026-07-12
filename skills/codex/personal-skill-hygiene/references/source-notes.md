# Source Notes

Checked: 2026-07-12.

This skill uses upstream material as design evidence, not as an authority over
the local Codex profile. Local authorization, host boundaries, specialist
routing, and recoverability take precedence.

## Sources

| Source | Pin or version | License/status | Adopted |
| --- | --- | --- | --- |
| [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills) | Live documentation checked 2026-07-11 | Official product documentation | Progressive disclosure; concise trigger descriptions; local skill structure; explicit disablement without deletion |
| [OpenAI: Build plugins](https://learn.chatgpt.com/docs/build-plugins) | Live documentation checked 2026-07-11 | Official product documentation | Distinguish local skill authoring from plugin packaging and distribution |
| [Superpowers `writing-skills` v6.1.1](https://github.com/obra/superpowers/tree/v6.1.1/skills/writing-skills) | Annotated tag object `c984ea2e7aeffdcc865784fd6c5e3ab75da0209a`; commit `d884ae04edebef577e82ff7c4e143debd0bbec99` | [MIT](https://github.com/obra/superpowers/blob/v6.1.1/LICENSE) | Progressive disclosure, trigger-focused descriptions, baseline/pressure testing for discipline skills, and captured rationalizations |
| Local `skill-creator` snapshot | `codex-cli 0.144.1`; home-relative path `~/.codex/skills/.system/skill-creator/SKILL.md`; SHA-256 `da44c88f6b3845a8fa8c60792ec9a722110a55a9793c279757b48fefb11f819c`; checked 2026-07-12 | Built-in Codex skill; current-host evidence snapshot only | Skill structure, metadata generation, validation, and independent forward-testing |
| Local `plugin-creator` snapshot | `codex-cli 0.144.1`; home-relative path `~/.codex/skills/.system/plugin-creator/SKILL.md`; SHA-256 `8fd56316b2c49cbdc657a5d197967a233018e1fada65b00a5dd030dce6499a6e`; checked 2026-07-12 | Built-in Codex skill; current-host evidence snapshot only | Plugin creation/update ownership and cachebuster/reinstall workflow |
| Local `skill-installer` snapshot | `codex-cli 0.144.1`; home-relative path `~/.codex/skills/.system/skill-installer/SKILL.md`; SHA-256 `d68b77e5bbb34dedab89d134da52855f140fc4b4299b80104f534e3b9e98f8ee`; checked 2026-07-12 | Built-in Codex skill; current-host evidence snapshot only | Curated and GitHub skill installation ownership |
| Local `personal-codex-hook-rules` | profile-kit revision `5ad41a7157352724ac51ad24f87949e3e23cc694`; repo path `skills/codex/personal-codex-hook-rules/SKILL.md`; Git blob `67c99c85ec7fc233b475e4e327bec02a5719ae39`; checked 2026-07-12 | Repository-exported personal profile skill | Codex hook authoring, protocol, validation, and trust-review ownership |

The three built-in entries are hash-addressed evidence snapshots of the current
host. They are not exported by profile-kit and are not distributed runtime
dependencies of this skill.

## Deliberately Rejected

- A universal Iron Law or mandatory test count for every skill edit.
- Mandatory delete-and-start-over behavior for an existing local skill.
- Mandatory commit, push, publication, or external installation during skill
  maintenance.
- Claude-specific plugin discovery, hook payload, invocation, or marketplace
  assumptions.
- Treating cache removal as equivalent to disablement or uninstallation.
- Splitting a skill solely because of length without distinct triggers, owners,
  or resource boundaries.

## Local Deviations

- Hygiene owns targeted lifecycle evidence and disposition, not general skill
  authoring, plugin creation, hook authoring, MCP authentication, or full-profile
  audit.
- Trust remains a native user-controlled state. This skill never edits a trust
  hash or infers trust from file presence.
- Destructive transitions are staged for recoverability and remain subject to
  the user's explicit authorization boundary.
- Testing is risk-tiered: metadata edits receive static checks, while trigger,
  discipline, and destructive behavior receive progressively stronger probes.
