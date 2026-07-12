# Source Notes

Checked: 2026-07-11

## Sources

| Source | License | Pinned version | Role |
| --- | --- | --- | --- |
| OpenAI Codex hooks documentation | Official documentation; no repository license asserted here | checked 2026-07-11 | Release behavior and trust guidance |
| OpenAI Codex generated hook schemas | Apache-2.0 | `rust-v0.144.1`, commit `44918ea10c0f99151c6710411b4322c2f5c96bea` | Exact native input and output wire format |
| Anthropic Claude Code Hookify `writing-rules` | MIT, as stated in the Hookify README | commit `15a21e1b4e240e2da6a4953d5f148a806c9c9bb2` | Historical Markdown rule design evidence only |
| Local controlled adapter and tests | Local profile | hooks stage accepted before this skill revision | Actual supported Markdown DSL and behavior |

Primary links:

- <https://developers.openai.com/codex/hooks>
- <https://github.com/openai/codex/tree/rust-v0.144.1/codex-rs/hooks/schema/generated>
- <https://github.com/anthropics/claude-code/blob/15a21e1b4e240e2da6a4953d5f148a806c9c9bb2/plugins/hookify/skills/writing-rules/SKILL.md>
- <https://github.com/anthropics/claude-code/blob/15a21e1b4e240e2da6a4953d5f148a806c9c9bb2/plugins/hookify/README.md>

## Adopted

From Codex:

- native config-layer discovery and project trust
- canonical `Bash`, `apply_patch`, and MCP tool names
- `tool_input.command` for Bash and `apply_patch`
- event-appropriate JSON output and exact-hash trust review
- the limitation that PreToolUse is a guardrail rather than complete enforcement

From Hookify:

- small Markdown files with YAML frontmatter
- simple regex or all-of conditions
- explicit enablement, action, and message body
- warnings about broad regexes and escaping

## Rejected

The following Hookify behavior is Claude-specific or incompatible with the local
adapter and is intentionally not carried forward:

- `.claude/` or project-local Markdown discovery
- `stop`, `prompt`, and `all` adapter events
- Claude Edit/Write/MultiEdit field semantics
- slash-command management and conversation analysis
- plain-text PreToolUse warnings
- catch-all completion rules and semantic writing enforcement

## Local Deviations

- The Markdown adapter is global-only and restricted to `bash/file` plus
  `warn/block`.
- Project hooks always use Codex native discovery and trust.
- Ordinary ask-first policies warn; only absolute deterministic prohibitions
  block.
- Detailed protocols live in references so the triggered SKILL.md remains small.
- No compatibility entry remains for the former generic skill name; the archived
  local folder is the recovery path.

## Refresh Policy

When Codex or Hookify changes:

1. Pin the new release, tag, or commit and record the check date.
2. Compare behavior, not wording.
3. Re-run local payload tests before adopting any protocol change.
4. Preserve deliberate local constraints unless the user approves a broader
   design change.
