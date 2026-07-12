# Codex Native Hook Reference

## Contents

- [Baseline And Freshness](#baseline-and-freshness)
- [Discovery And Trust](#discovery-and-trust)
- [PreToolUse Matching](#pretooluse-matching)
- [PreToolUse Input](#pretooluse-input)
- [PreToolUse Output](#pretooluse-output)
- [Other Native Events](#other-native-events)
- [Limits](#limits)

## Baseline And Freshness

The locally validated baseline is Codex CLI `0.144.1`, release tag
`rust-v0.144.1`, commit `44918ea10c0f99151c6710411b4322c2f5c96bea`.

Before changing event-specific behavior:

1. Run `codex --version`.
2. If the version differs, consult the current official hooks documentation and
   the generated schemas for that exact release.
3. Update `source-notes.md` before adopting changed fields or semantics.

The `main` branch schemas may be newer than the installed release. Treat the
installed release and its matching generated schema as the wire-format baseline.

## Discovery And Trust

Codex discovers native hooks alongside active config layers:

- user: `~/.codex/hooks.json` or `~/.codex/config.toml`
- project: `<repo>/.codex/hooks.json` or `<repo>/.codex/config.toml`
- plugin: the enabled plugin's declared hook source or `hooks/hooks.json`

Matching hooks from different sources are additive. Multiple matching command
handlers may start concurrently, so one handler cannot prevent another matching
handler from starting.

Project hooks load only when the project `.codex/` layer is trusted. Every
non-managed command hook definition is trusted by its current hash. After a
definition changes, leave the hash alone and ask the user to review it with
`/hooks`.

Prefer one representation per config layer. If a layer contains both
`hooks.json` and inline `[hooks]`, Codex merges them and warns.

## PreToolUse Matching

`matcher` is a regex over the canonical tool name and supported aliases. Current
canonical values relevant to this profile are:

- `Bash`
- `apply_patch`
- MCP names such as `mcp__server__tool`

For `apply_patch`, matcher aliases may include `Edit` or `Write`, but the payload
still reports `tool_name: "apply_patch"`.

The local adapter intentionally registers exact matchers `^Bash$` and
`^apply_patch$`.

## PreToolUse Input

The `0.144.1` command payload includes the common session fields plus the
event-specific tool fields. Bash and `apply_patch` place their text in
`tool_input.command`:

```json
{
  "session_id": "test-session",
  "transcript_path": null,
  "cwd": "/tmp",
  "hook_event_name": "PreToolUse",
  "model": "test-model",
  "permission_mode": "default",
  "turn_id": "test-turn",
  "tool_name": "Bash",
  "tool_use_id": "test-call",
  "tool_input": {"command": "printf test"}
}
```

MCP tools send their arguments object in `tool_input`; do not force the command
shape onto MCP payloads.

## PreToolUse Output

Exit `0` with no stdout to allow the call without adding context.

Return model-visible warning context as one JSON object:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "additionalContext": "The pending command needs an explicit environment."
  }
}
```

Return a deterministic denial as one JSON object:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Editing this credential-bearing file is blocked."
  }
}
```

Plain text on stdout is ignored for `PreToolUse`. Do not emit explanatory text
before or after the JSON object. Use stderr for handler diagnostics that must not
corrupt stdout.

Do not use `permissionDecision: "ask"`, input rewriting, legacy shapes, or
event-generic continuation fields merely because a schema parses them. Verify
that the installed release implements the required semantics first.

## Other Native Events

Native Codex supports more events than the local Markdown adapter. For a request
involving `PermissionRequest`, `PostToolUse`, `Stop`, prompt submission,
compaction, session, or subagent events, read the current official event section
and matching release schema before writing the handler.

Do not use a native Stop hook for a generic completion checklist. Completion
evidence belongs to the final verification workflow unless the user has a
specific, deterministic continuation requirement.

## Limits

`PreToolUse` is a guardrail, not a complete security boundary. Coverage varies by
tool path, and equivalent work may be possible through an uncovered tool. State
that limitation whenever a rule is described as blocking an operation.
