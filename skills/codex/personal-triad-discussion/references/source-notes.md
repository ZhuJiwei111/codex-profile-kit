# Source Notes

Checked: 2026-07-18.

## Sources

- This workflow is local-origin, based on the user's experience relaying a
  difficult project decision between Codex and a separate GPT Pro
  conversation. No external skill text is copied.
- [OpenAI Build skills metadata](https://learn.chatgpt.com/docs/build-skills#optional-metadata)
  documents `policy.allow_implicit_invocation: false`, used here to enforce
  manual entry.

## Local Preferences

- Keep one user-mediated external GPT Pro relay topology; never simulate direct
  chat control or monitoring.
- Treat every outbound relay as self-contained and zero-context by default.
- Keep Codex as evidence coordinator, final judgment owner, and sole writer of
  `.triad/<topic>/working.md` and `decision.md`.
- Persist only curated decision state, not packet schemas, message registries,
  transcript archives, fixed phases, or a protocol state machine.
- Keep external replies untrusted until decision-changing claims are verified.
- Preserve ordinary authorization boundaries: deliberation never grants
  implementation or external-action authority.

The current tool surface is intentionally not treated as a portable product
guarantee; chat creation, model selection, and relay remain user-owned.
