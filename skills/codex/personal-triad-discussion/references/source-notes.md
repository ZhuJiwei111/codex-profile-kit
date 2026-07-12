# Source Notes

Checked: 2026-07-12.

This skill is local-origin and grew from the user's experience coordinating a
complex project discussion between Codex and a GPT Pro conversation during an
architecture and project-purpose bottleneck. No external skill text is copied,
and no external derivative-license claim is made. Current official OpenAI
documentation is used as product-behavior evidence, not as the source of the
local deliberation method.

## Contents

- [Local History](#local-history)
- [Official Product Evidence](#official-product-evidence)
- [Current Tool-Surface Evidence](#current-tool-surface-evidence)
- [Baseline Probes](#baseline-probes)
- [Adopted](#adopted)
- [Rejected Or Retired](#rejected-or-retired)
- [Local Deviations And Limits](#local-deviations-and-limits)

## Local History

- Initial profile-kit commit:
  `d81e3f4ea1a63c2fffd45320e30f018cb2d38a94`
- Initial `SKILL.md` blob:
  `7931e24ad3b18bf0b1288091c07278f81cfe8b05`
- Initial `agents/openai.yaml` blob:
  `57a71d6a9d3897da053ed4203e8b789dd909aab2`
- Live-context expansion commit:
  `eceeca04ada43a7efa19e6c1ca495e4caab30f30`
- Pre-rewrite `SKILL.md` blob:
  `960e97adbf37bfc7606f5713b0ccaf5aebe5586a`
- Pre-rewrite `agents/openai.yaml` blob:
  `72e77e0948875f7ac132dd9b31084726f2abac98`

The initial skill preserved useful role and authorization boundaries but grew
into a fixed meeting protocol with mandatory message identifiers, status
headers, phase approvals, local live-context files, and formal phase summaries.

## Official Product Evidence

- [Projects, chats, and tasks](https://learn.chatgpt.com/docs/projects)
  distinguishes ordinary Quick Chat from Work and Codex tasks, describes
  ChatGPT Projects and local projects, and documents bringing a Quick Chat into
  a current task when the UI offers `Add to task`.
- [Projects in ChatGPT](https://help.openai.com/en/articles/10169521-projects-in-chatgpt)
  documents Project instructions, files, moving eligible chats into a Project,
  and the difference between default and project-only memory.
- [Build skills](https://learn.chatgpt.com/docs/build-skills#optional-metadata)
  documents `policy.allow_implicit_invocation: false` for explicit-only skill
  invocation.
- [Slash commands](https://learn.chatgpt.com/docs/reference/slash-commands#available-slash-commands)
  defines `/side` as a temporary side conversation and `/fork` as a copied
  local task or worktree rather than an external GPT participant.

These pages are current product documentation rather than commit-pinned source.
Recheck them when Project, chat import, skill invocation, or task coordination
behavior changes.

## Current Tool-Surface Evidence

During this revision, the current Codex task did not expose a product tool that
could create or control a user-owned GPT Pro chat inside a ChatGPT Project. This
is a statement about the observed session tool surface, not a universal product
limitation. The approved workflow therefore keeps Project-chat creation, model
selection, and message relay user-mediated.

The revision excludes a live GPT Pro Project-chat smoke test. Native import or
add-to-task behavior remains conditional on what the current UI actually
exposes; copy or a labeled excerpt is the reliable relay fallback.

## Baseline Probes

A read-only explicit-invocation probe against the pre-rewrite skill produced a
mandatory status header, phase and message identifiers, a seven-question GPT
prompt, a phase-summary commitment, and a future local-live-context path before
the project facts were known. This supported removing the fixed protocol.

A neighboring lightweight-discussion probe correctly stayed with
`personal-brainstorms` when the user explicitly rejected a triad workflow. The
new explicit-only policy makes that separation mechanical rather than relying
on the user to negate the older broad trigger.

## Adopted

- Manual-only invocation.
- One topology: a new user-created GPT Pro chat inside the target ChatGPT
  Project.
- User-mediated relay and no polling or monitoring of the GPT Pro chat.
- Procedural independence through a neutral first brief and explicit separation
  of facts, Project context, assumptions, and inferences.
- A flexible decision loop: independent reframe, disagreement mapping, targeted
  exchange, and decision synthesis.
- Three context layers: curated GPT Pro input, a bounded Codex coordinator task,
  and independent evidence work when collection itself becomes substantial.
- One kickoff brief, event-driven checkpoints, optional same-Project restart,
  and a final decision synthesis.

## Rejected Or Retired

- Project-external Quick Chat as an alternative initialization path.
- A permanent adversarial-reviewer role for GPT Pro.
- Mandatory `U/G/C/E/LC/S/H` identifiers and required status headers.
- Fixed phases, mandatory phase summaries, or approval before every phase move.
- Approval before bounded in-scope read-only inspection.
- Automatic worker or subagent use for ordinary evidence checks.
- Local `live_context.md`, discussion directories, archives, or formal handoff
  files created by default.
- Treating `/side`, `/fork`, a Codex subagent, or a worktree worker as the third
  GPT participant.
- Treating external consensus as implementation or resource authorization.

## Local Deviations And Limits

- The user remains the only chair and final decision owner. Codex coordinates
  evidence and synthesis; GPT Pro provides independent reasoning material.
- Project memory provides continuity but not guaranteed retrieval or physical
  context isolation. The skill mitigates anchoring procedurally and does not
  modify the Project memory mode.
- Global instructions retain ownership of user-change protection, secrets,
  resources, long jobs, Git, external effects, and ask-first boundaries.
- `personal-brainstorms` and explicitly invoked `personal-grilling` own internal
  design shaping and decision-changing questions. Context, delegation,
  debugging, persistence, planning, explanation, and final verification remain
  with their specialist skills.
- No mechanical validator or reusable script is bundled. Profile validators,
  metadata checks, link checks, stale-protocol searches, and isolated behavior
  probes are more proportionate to this qualitative workflow.
