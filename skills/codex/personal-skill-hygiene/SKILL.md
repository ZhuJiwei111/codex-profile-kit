---
name: personal-skill-hygiene
description: Use when auditing, creating, editing, enabling, disabling, archiving, or installing Codex or Claude skills, plugins, MCP servers, hooks, or workflow configuration.
---

# Personal Skill Hygiene

Keep skills narrow, light, and recoverable. Prefer project rules, scripts, tests,
and acceptance criteria over broad workflow prompts.

## Audit

- Inspect enabled plugin/config state before judging cache directories.
- Separate active skills, disabled plugin caches, and archived copies.
- Identify wide triggers: “any conversation”, “always”, “before any action”,
  broad workflow summaries, or large generic process bodies.
- Treat credentials, auth files, tokens, cookies, and private keys as sensitive.

## Clean

- Disable or remove broad plugins before deleting cache.
- Archive local skills before removal; do not delete the only copy by default.
- Replace repeated personal workflows with multiple small skills, each with a
  narrow `Use when...` description and a short body.
- Validate edited skills and report exact archive paths.
