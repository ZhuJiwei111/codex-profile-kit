# Source Notes

Checked: 2026-07-18.

The deterministic local sources are this repository's `scripts/sync.py`,
`README.md`, and `INSTALL.md`. They define audit/export/apply commands,
transactional backup behavior, and Python 3.11+ requirements.

Key local preferences are four explicit manual intents, current-host scope,
portable `AGENTS.md`, `personal-*` skills, and only other explicitly inventoried
targets. Non-personal skills, host-local/configuration/credential/runtime state,
and custom agent profiles stay outside the managed payload. The only lifecycle
exception is backup and removal of the exact retired paths listed by sync.py,
including the former monitor/reviewer TOMLs. GitHub synchronization runs
audit/export and semantic verification before an exact `commit + push` handoff
to `personal-branch-finish`; `scripts/sync.py` performs no Git action. Inbound
apply also ends with semantic final verification rather than a fixed token.

Outbound export is a conservative overlay rather than an absence-driven mirror:
repo-only personal entries survive, and the repository-owned hooks template is
not reconstructed from the active rendered hooks.json.

The one-time Hookify retirement also accounts for task-local hook-definition
caching: tool-dependent work finishes before deleting a loaded command, and a
fresh bounded executor performs the final audit without retaining a shim.
