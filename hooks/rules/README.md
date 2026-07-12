# Controlled Global Markdown Hook Rules

This directory contains small, deterministic rules evaluated by
`~/.codex/hooks/hookify_codex_runner.py` for Codex `PreToolUse` events.

## Scope

- `event: bash` matches only canonical `tool_name: "Bash"` payloads.
- `event: file` matches only canonical `tool_name: "apply_patch"` payloads.
- Rules may use `action: warn` or `action: block`.
- `warn` emits `hookSpecificOutput.additionalContext`.
- `block` emits `permissionDecision: "deny"` with a reason.
- Prompt, Stop, PostToolUse, and catch-all rules are intentionally unsupported.

Only Markdown files in this directory are loaded. Do not place project policy
here or under a project's legacy Hookify paths. Use native project
`.codex/hooks.json` or `.codex/config.toml` so Codex discovery and trust apply.

## Rule Shape

```markdown
---
name: warn-example
enabled: true
event: bash
action: warn
pattern: example-command
---

Short action-oriented context for Codex.
```

Instead of `pattern`, a rule may use `conditions`. Supported fields are
`command`, `file_path`, `content`, `patch`, `new_text`, `old_text`, `tool_name`,
and `all`. Supported operators are `regex_match`, `regex_not_match`, `contains`,
`not_contains`, `equals`, `starts_with`, and `ends_with`. All conditions must
match.

Rule names must be unique kebab-case. Invalid rules are reported on stderr and
cannot prefix or corrupt the single JSON object written to stdout.

## Validation

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s ~/.codex/hooks -p 'test_*.py' -v
```

Changing `hooks.json` requires review through `/hooks`. Do not edit persisted
trust hashes manually.
