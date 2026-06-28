# Migration Manifest

Generated for a clean Codex profile kit.

## Included

- `rules/AGENTS.portable.md`: machine-neutral durable Codex behavior rules.
- `templates/HOST_LOCAL_TEMPLATE.md`: target-machine overlay template.
- `templates/hooks.json.template`: Codex hook wiring template with placeholders.
- `templates/config.toml.template`: minimal portable Codex config reference.
- `skills/codex/`: non-system custom Codex skills from `~/.codex/skills`.
- `skills/agents/find-skills/`: portable agent skill discovery helper.
- `hooks/scripts/`: hook scripts and tests from `~/.codex/hooks`.
- `hooks/rules/`: Hookify markdown rules from `~/.codex/hookify`.
- `hooks/docs/smart-commit.md`: smart-commit hook notes with templated paths.
- `CONNECTORS.md`: re-authentication checklist for plugins/connectors.
- `INSTALL.md`: target-machine install and smoke-test guide.

## Excluded

- Codex auth files, tokens, connector OAuth state, cookies, passwords, and
  secrets.
- Session history, archived sessions, logs, attachments, and pasted files.
- SQLite databases, WAL/SHM files, state databases, and goal/history stores.
- Codex memories and rollout summaries.
- Plugin caches, app caches, marketplace temporary clones, and model caches.
- Project trust lists, hook trusted hashes, approval history, and local runtime
  state.
- Conda environments, package caches, datasets, model weights, project outputs,
  and machine-specific tool installations.
