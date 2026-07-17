# Migration Manifest

This manifest defines the repository's current portable boundary.

## Managed Synchronization Payload

- `rules/AGENTS.portable.md`: the complete machine-neutral
  `~/.codex/AGENTS.md`; confirmed apply backs up and replaces the whole file.
- `skills/codex/personal-*`: personal Codex workflow skills only.
- `agents/codex/`: custom Codex agent profiles in the explicit managed
  inventory.
- `hooks/scripts/` and `hooks/rules/`: hook code, tests, and controlled global
  Markdown rules in the explicit managed inventory.
- `templates/hooks.json.template`: wiring source for the managed hooks.

Target-host non-personal Codex skills and `~/.agents/skills` are preserved and
excluded from audit drift.

## Repository References

- `templates/HOST_LOCAL_TEMPLATE.md`: starting point for host-local facts.
- `templates/REMOTE_CONNECTION_EXAMPLE.md`: static, credential-free connection
  example; synchronization never populates it from the active host.
- `templates/config.toml.template`: manual configuration reference without
  target-host auth or runtime state.
- `INSTALL.md`: inbound fetch/integrate, dry-run, confirmed apply, and
  post-apply audit flow.
- `CONNECTORS.md`: target-host reconnection checklist.

## Host-Local Or Excluded

- `HOST_LOCAL.md`, `config.toml`, connection contracts, auth files, tokens,
  cookies, passwords, and connector or MCP session state.
- Session history, logs, attachments, SQLite state, goal/history stores,
  memories, and rollout summaries.
- Plugin and app caches, marketplace clones, model caches, project trust,
  hook trusted hashes, approval history, and other runtime state.
- Environments, package caches, datasets, model weights, project outputs, and
  machine-specific tools.
