# Controlled Global Markdown Adapter

## Contents

- [Scope](#scope)
- [Rule Shape](#rule-shape)
- [Conditions](#conditions)
- [Actions And Precedence](#actions-and-precedence)
- [File Rule Example](#file-rule-example)
- [Rejected Legacy Behavior](#rejected-legacy-behavior)

## Scope

The adapter source of truth is `~/.codex/hooks/hookify_codex_runner.py`. It loads
only `*.md` files directly under `~/.codex/hookify/`; it skips `README.md`.

| Rule event | Canonical tool | Matched text |
| --- | --- | --- |
| `bash` | `Bash` | `tool_input.command` |
| `file` | `apply_patch` | `tool_input.command` containing the patch |

Supported actions are `warn` and `block`. Unsupported tools and events are
ignored. A supported tool with a malformed command payload returns a JSON
`systemMessage` rather than guessing at another field.

Do not place adapter rules in a project. Use `<repo>/.codex/hooks.json` or
`<repo>/.codex/config.toml` so native project discovery and trust apply.

## Rule Shape

Use one of `pattern` or `conditions`, never both:

```markdown
---
name: warn-example-command
enabled: true
event: bash
action: warn
pattern: (^|\s)example-tool\s+--unsafe(?:\s|$)
---

Confirm the intended scope before using the unsafe option.
```

Required behavior:

- `name`: unique kebab-case among enabled rules
- `enabled`: boolean; defaults to `true`
- `event`: `bash` or `file`
- `action`: `warn` or `block`; defaults to `warn`
- message body: non-empty and action-oriented
- exactly one non-empty `pattern` or `conditions` list

Unknown frontmatter fields, invalid regexes, duplicate enabled names, and invalid
conditions are diagnostics. They do not prefix stdout or silently become a
different rule.

## Conditions

Each condition has `field`, `operator`, and `pattern`. All conditions must match.

Supported operators:

- `regex_match`
- `regex_not_match`
- `contains`
- `not_contains`
- `equals`
- `starts_with`
- `ends_with`

Current field mapping:

| Field | Bash | File |
| --- | --- | --- |
| `all` | command | entire patch command |
| `command` | command | empty |
| `content` | command | entire patch command |
| `file_path` | empty | newline-separated paths extracted from `*** Add/Update/Delete File:` headers |
| `new_text` | empty | entire patch command |
| `old_text` | empty | empty |
| `patch` | empty | entire patch command |
| `tool_name` | `Bash` | `apply_patch` |

This mapping is intentionally not Claude Edit/Write semantics. In particular,
do not write a rule that expects `old_text` to contain removed content, and do
not assume `new_text` is only the added lines.

A simple `pattern` matches `command` for `bash` and `all` for `file`.

## Actions And Precedence

- `warn` returns `hookSpecificOutput.additionalContext`.
- `block` returns `permissionDecision: "deny"` and a reason.
- If any matching rule blocks, the combined block output takes precedence over
  all matching warnings.
- Multiple messages of the winning action are joined into one JSON response.
- No match produces no stdout.

Use `block` only for narrow, deterministic prohibitions such as editing an
absolute credential-bearing file category. Use `warn` for ordinary ask-first
context where the model can stop and request user approval.

## File Rule Example

```markdown
---
name: block-example-private-key
enabled: true
event: file
action: block
conditions:
  - field: file_path
    operator: ends_with
    pattern: example-private-key.pem
---

Editing private-key material through the ordinary workflow is blocked. Use the
dedicated user-controlled credential mechanism.
```

Use synthetic paths in examples and tests. Never place an actual key, token,
cookie, authenticated URL, or secret value in a rule body or fixture.

## Rejected Legacy Behavior

Do not create or document these adapter features:

- `event: stop`, `event: prompt`, or `event: all`
- project `.codex/hookify*.md` or `.codex/hookify/*.md` discovery
- Claude `Edit`, `Write`, or `MultiEdit` payload assumptions
- plain-text PreToolUse warnings
- catch-all `pattern: .*` completion reminders
- automatic Git staging or semantic writing/discussion enforcement
