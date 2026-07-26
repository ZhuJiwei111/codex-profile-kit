# Source Notes

Checked: 2026-07-18.

## Source

- OpenAI's live [Prompting guidance for GPT-5.6
  Sol](https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6),
  fetched from the official developer documentation on 2026-07-18: outcome-first
  prompting, removal of repeated instructions and irrelevant examples or tools,
  preservation of completion and authorization boundaries, decision rules over
  unnecessary absolutes, representative evaluation, and surgical migration.

The official guide is current product guidance, not a runtime dependency. Its
performance figures and model-specific capabilities are intentionally not
embedded as stable local rules.

## Local Preferences

- Keep manual-only Repair and Handoff modes.
- Support three entry scenarios: an existing zero-context prompt, invocation
  from `/side` with visible context, and a side discussion compiled for a new
  task.
- Default the recipient to a fresh zero-context Codex task.
- Use stable prompt principles locally; consult current official documentation
  only for latest/default model questions or migration work.
- Return one executable prompt by default and ask at most one smallest material
  question when required.
- Preserve authorization, evidence limits, locked literals, and source language;
  never claim static improvement or execute the prompt while transforming it.

No official template or substantial prose is copied.
