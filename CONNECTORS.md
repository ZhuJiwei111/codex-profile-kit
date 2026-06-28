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

## Smoke Check

Ask Codex to summarize available connector capabilities without printing secret
values. If a connector fails, repair the target-machine installation rather than
copying old state.
