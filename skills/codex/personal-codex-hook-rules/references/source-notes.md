# Source Notes

Checked: 2026-07-12

## Sources

| Source | License | Pinned version | Role |
| --- | --- | --- | --- |
| OpenAI Codex hooks documentation | Official documentation; no repository license asserted here | checked 2026-07-11 | Release behavior and trust guidance |
| OpenAI Codex generated hook schemas | Apache-2.0 | `rust-v0.144.1`, commit `44918ea10c0f99151c6710411b4322c2f5c96bea` | Exact native input and output wire format |
| Anthropic Claude Code Hookify `writing-rules` | MIT, as stated in the Hookify README | commit `15a21e1b4e240e2da6a4953d5f148a806c9c9bb2` | Historical Markdown rule design evidence only |
| Local controlled Markdown adapter | Local profile | profile-kit revision `5ad41a7157352724ac51ad24f87949e3e23cc694`; repo path `hooks/scripts/hookify_codex_runner.py`; Git blob `b00b24d278a37a170d31c4b7e8a5d6eb6c36116c`; checked 2026-07-12 | Actual supported Markdown DSL and behavior |
| Local adapter behavior tests | Local profile | profile-kit revision `5ad41a7157352724ac51ad24f87949e3e23cc694`; repo path `hooks/scripts/test_hookify_codex_runner.py`; Git blob `557c42d6532a741bf632bb22684f384d4dc0bcc1`; checked 2026-07-12 | Executable evidence for adapter payload, rule, and decision behavior |
| Local hook configuration tests | Local profile | profile-kit revision `5ad41a7157352724ac51ad24f87949e3e23cc694`; repo path `hooks/scripts/test_hooks_configuration.py`; Git blob `66dd971965b2b42d91f4c63cbe8f598a51739a12`; checked 2026-07-12 | Executable evidence for adapter discovery and configured hook wiring |

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

```yaml
skill_admission:
  skill: personal-codex-hook-rules
  acquisition_mode: created
  source_classification: hybrid
  provenance_status: complete
  admission_status: admitted
  portability_disposition: internalized
  safety_status: passed
  safety_review: "static_pass: Native hook and Markdown-guard mutation stays behind exact authority, payload validation, trust review, and no-credential boundaries; this skill bundles no executable of its own."
  trigger_status: passed
  trigger_review: "static_pass: Codex hook and controlled Markdown guard ownership was reviewed against generic configuration, skill hygiene, and whole-profile audit routes."
  validation_status: passed
  validation:
    - "static_pass: Pinned schemas, Hookify design source, local adapter blobs, and behavior-test evidence reviewed on 2026-07-16."
    - "static_pass: Targeted personal-skill admission validator fixtures passed on 2026-07-16."
  update_owner: "maintainer of personal-codex-hook-rules"
  update_rule: "Repeat provenance, safety, trigger, trust, payload, and portability review before any source, hook protocol, adapter, or ownership change enters portable export."
  rollback_basis: "Remove the skill through personal-skill-hygiene and restore the reviewed tree from codex-profile-kit revision 3791645f59c0eeec497755bd7301be78b44efbea."
  unknowns_disposition: none
  unknowns: []
```
