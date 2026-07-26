# Source Notes

Checked: 2026-07-18.

## Upstream Design Source

- Project: Anthropic official Claude plugins
- Repository: https://github.com/anthropics/claude-plugins-official
- Fixed commit: 6fbe3b01859cc0c4e84ba66028cffd91f2b02d93
- Source:
  https://github.com/anthropics/claude-plugins-official/blob/6fbe3b01859cc0c4e84ba66028cffd91f2b02d93/plugins/code-simplifier/agents/code-simplifier.md
- License: Apache License 2.0.

The source is design evidence, not a runtime dependency. The local skill does
not inherit Claude model, plugin, or autonomous post-edit cleanup behavior.

## Local Preferences

- Trigger only for explicit bounded simplification or an authorized scoped
  cleanup handoff.
- Preserve observable behavior and protected user work.
- Use the same focused baseline before and after the change.
- Prefer clarity and maintainability over fewer lines.
- Do not infer dead code from missing direct calls.
- Keep behavior changes, broad formatting, dependencies, configuration, Git,
  and publication outside cleanup.
