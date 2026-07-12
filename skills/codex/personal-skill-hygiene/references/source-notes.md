# Source Notes

Checked: 2026-07-11.

This skill uses upstream material as design evidence, not as an authority over
the local Codex profile. Local authorization, host boundaries, specialist
routing, and recoverability take precedence.

## Sources

| Source | Pin or version | License/status | Adopted |
| --- | --- | --- | --- |
| [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills) | Live documentation checked 2026-07-11 | Official product documentation | Progressive disclosure; concise trigger descriptions; local skill structure; explicit disablement without deletion |
| [OpenAI: Build plugins](https://learn.chatgpt.com/docs/build-plugins) | Live documentation checked 2026-07-11 | Official product documentation | Distinguish local skill authoring from plugin packaging and distribution |
| [Superpowers `writing-skills` v6.1.1](https://github.com/obra/superpowers/tree/v6.1.1/skills/writing-skills) | Annotated tag object `c984ea2e7aeffdcc865784fd6c5e3ab75da0209a`; commit `d884ae04edebef577e82ff7c4e143debd0bbec99` | [MIT](https://github.com/obra/superpowers/blob/v6.1.1/LICENSE) | Progressive disclosure, trigger-focused descriptions, baseline/pressure testing for discipline skills, and captured rationalizations |
| Local `skill-creator` | Current host copy checked 2026-07-11 | Built-in Codex skill | Skill structure, metadata generation, validation, and independent forward-testing |
| Local `plugin-creator` | Current host copy checked 2026-07-11 | Built-in Codex skill | Plugin creation/update ownership and cachebuster/reinstall workflow |
| Local `skill-installer` | Current host copy checked 2026-07-11 | Built-in Codex skill | Curated and GitHub skill installation ownership |
| Local `personal-codex-hook-rules` | Accepted local revision checked 2026-07-11 | Personal profile skill | Codex hook authoring, protocol, validation, and trust-review ownership |

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
