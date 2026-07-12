# Connector Reconnection Checklist

Do not copy connector auth state, OAuth tokens, cookies, app caches, or plugin
caches from the source machine.

## GitHub Plugin

- Install or enable the GitHub plugin on the target machine.
- Re-authenticate through the target Codex UI or CLI flow.
- Verify repository access with a low-risk metadata read before using PR or
  issue workflows.

## Other Connectors

- Reinstall connectors from trusted sources on the target machine.
- Re-authenticate interactively.
- Keep credentials out of `AGENTS.md`, skills, hooks, templates, and migration
  reports.

## Portable MCP Servers

- Review the public, secret-free MCP declarations in
  `templates/config.toml.template` and merge only the servers intended for the
  target host.
- The template may carry a public endpoint identity and enabled state. Recreate
  environment bindings or interactive authentication on the target machine;
  never copy credential values, authenticated headers, or runtime auth state.
- Verify each configured server with a low-risk capability or metadata read.

## Smoke Check

Ask Codex to summarize available connector capabilities without printing secret
values. If a connector fails, repair the target-machine installation rather than
copying old state.
