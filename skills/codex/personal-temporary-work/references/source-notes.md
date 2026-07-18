# Source Notes

Checked: 2026-07-18.

This skill is local-origin and reflects the user's recurring need to keep
one-time conversion and repair logic out of maintained runtime code. No
external skill text is copied.

Official Codex skill guidance informed the concise, instruction-first structure:

- https://learn.chatgpt.com/docs/build-skills
- https://learn.chatgpt.com/docs/customization/overview#skills

## Local Preferences

- Distinguish durable, temporary, and hybrid work.
- Default disposable work to a safe task-specific temporary directory.
- Use project-local scratch only for recovery, reattachment, audit, or handoff.
- Do not automatically edit .gitignore or other tool configuration.
- Keep canonical inputs immutable and formal deliverables separate from scratch.
- Let Codex remove only exact current-task scratch that it created and no longer
  needs.
- Retain scratch when failure recovery, reproduction, retry, audit, or handoff
  still benefits from it.
- A retained helper needs only purpose, inputs, outputs, use, and delete
  condition.
