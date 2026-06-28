---
name: warn-project-output-explainer-style-on-stop
enabled: true
event: stop
action: warn
pattern: .*
---

For user-visible project plans, implementation plans, diagnostic summaries,
handoffs, review notes, artifact status, pipeline outputs, or implementation
reports, answer in Chinese with the `personal-project-output-explainer` style:
state the gist, separate facts/risks/judgment, explain consequences, and give
one lightweight recommendation when evidence supports it.

This still applies when the work is about creating or editing Codex-facing
artifacts such as `AGENTS.md`, `SKILL.md`, plugin metadata, or workflow notes:
keep the surrounding plan/explanation in Chinese, while keeping the artifact
content itself in English.

Skip this for tiny answers, simple command output, code review findings, low-level
debugging, CI localization, live long-job status, or explicit alternate formats.
