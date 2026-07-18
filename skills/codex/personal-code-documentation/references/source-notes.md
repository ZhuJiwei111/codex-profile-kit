# Source Notes

Checked: 2026-07-18.

This skill combines two design sources. They are evidence for the local
workflow, not runtime dependencies.

## Code Documentation Source

- Repository: https://github.com/wshobson/agents
- Fixed commit: 2de74ac1c8f6669821dcef13153332c3168033c1
- Relevant subtree:
  https://github.com/wshobson/agents/tree/2de74ac1c8f6669821dcef13153332c3168033c1/plugins/code-documentation
- License: MIT, Copyright 2024 Seth Hobson.

The local skill retains audience-first structure, bounded source discovery, and
tutorial outcomes with checkpoints. It does not retain Claude agent, model,
command, mandatory outline, visual, or code-explanation protocols.

## Existing-Documentation Sync Source

- Repository: https://github.com/openai/openai-agents-js
- Fixed comparison commit: 901fb94c0fb9ffc8cb2d8275d99622475f77f401
- Source skill:
  https://github.com/openai/openai-agents-js/blob/901fb94c0fb9ffc8cb2d8275d99622475f77f401/.agents/skills/docs-sync/SKILL.md
- License: MIT, Copyright 2025 OpenAI.

The exact historical commit that first shaped the retired local docs-sync skill
is not established. The fixed comparison above is the retained provenance
baseline.

## Local Preferences

- Keep only document, with tutorial as a subtype, and sync_existing.
- Do not own conversational code explanation.
- Use bounded source evidence and respect generated-document ownership.
- Verify examples when practical and label unrun examples.
- Keep sync_existing to the smallest factual patch after an identified contract
  change.
