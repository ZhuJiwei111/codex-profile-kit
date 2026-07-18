# Source Notes

Checked: 2026-07-18

## Sources

| Source | License | Pinned version | Role |
| --- | --- | --- | --- |
| OpenAI Codex hooks documentation | Official documentation; no repository license asserted here | checked 2026-07-18 | Current event, matcher, payload, output, concurrency, and trust behavior |
| OpenAI Codex generated hook schemas | Apache-2.0 | `rust-v0.144.1`, commit `44918ea10c0f99151c6710411b4322c2f5c96bea` | Exact native input and output wire format |
| Local native handlers and tests | Local profile | `hooks/scripts/`; checked 2026-07-18 | Portable safety behavior and configuration wiring |

Primary links:

- <https://developers.openai.com/codex/hooks>
- <https://github.com/openai/codex/tree/rust-v0.144.1/codex-rs/hooks/schema/generated>

## Adopted

From Codex:

- native config-layer discovery and project trust
- canonical `Bash`, `apply_patch`, and MCP tool names
- `tool_input.command` for Bash and `apply_patch`
- event-appropriate JSON output and exact-hash trust review
- the limitation that PreToolUse is a guardrail rather than complete enforcement

The former Hookify-derived Markdown adapter was retired in favor of direct
native handlers. The profile retains only the three narrow deterministic safety
checks and the stateless large-download advisory.

## Local Deviations

- User and project hooks use Codex native discovery and trust.
- Ordinary ask-first policies warn; only absolute deterministic prohibitions
  block.
- Detailed protocols live in references so the triggered SKILL.md remains small.

## Refresh Policy

When Codex changes:

1. Pin the new release, tag, or commit and record the check date.
2. Compare behavior, not wording.
3. Re-run local payload tests before adopting any protocol change.
4. Preserve deliberate local constraints unless the user approves a broader
   design change.
