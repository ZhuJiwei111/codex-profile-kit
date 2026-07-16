# Source Notes

Checked: 2026-07-16.

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
- The user is the low-frequency decision and authority owner, not the per-round
  chair, analyst, or recorder.
- The Codex main process is the control plane for opening summaries, relays,
  sole memo writing, bounded delegation, compressed synthesis, direct user
  requests, and final judgment; substantial evidence work belongs to a bounded
  subagent or worker.
- A five-line opening summary and one explicit user-action label per visible
  round, with exact action, reason, impact, and success signal when intervention
  is required.
- Procedural independence through a neutral first brief and explicit separation
  of facts, Project context, assumptions, and inferences.
- A flexible decision loop: independent reframe, disagreement mapping, targeted
  exchange, and decision synthesis.
- Three context layers: curated GPT Pro input, a bounded Codex coordinator task,
  and independent evidence work when collection itself becomes substantial.
- One kickoff brief, event-driven checkpoints, Continuity Restart or Blank
  Restart as distinct modes, and a final decision synthesis.
- One coordinator-written project memo for an explicitly invoked multi-round
  discussion. Prefer an existing decision-note convention; otherwise use
  `.triad/<topic-slug>/working.md` and `decision.md`.
- Update working state after material rounds and curate a transcript-free final
  decision. GPT Pro and subagents never write the memo.

## Rejected Or Retired

- Project-external Quick Chat as an alternative initialization path.
- A permanent adversarial-reviewer role for GPT Pro.
- Mandatory `U/G/C/E/LC/S/H` identifiers and required status headers.
- Fixed phases, mandatory phase summaries, or approval before every phase move.
- Approval before bounded in-scope read-only inspection.
- Automatic worker or subagent use for ordinary evidence checks.
- Fixed phase documents, message registries, transcript archives, or a generic
  `live_context.md`. The later bounded topic memo supersedes this earlier
  rejection and exists only after explicit multi-round invocation.
- Treating `/side`, `/fork`, a Codex subagent, or a worktree worker as the third
  GPT participant.
- Treating external consensus as implementation or resource authorization.
- Treating the user as the per-round chair, analyst, recorder, or a mandatory
  `continue` signal between GPT Pro replies.
- Letting the main process absorb repository exploration, multi-file source or
  log analysis, or test and experiment evidence when a bounded evidence worker
  is required but unavailable.

## Local Deviations And Limits

- The user remains the final decision and authority owner but is deliberately
  not the per-round chair. Codex coordinates evidence and synthesis; GPT Pro
  provides independent reasoning material.
- Project memory provides continuity but cannot guarantee isolation or
  retrieval. A Blank Restart therefore creates a new chat and sends no working
  memo, verified state, or old conclusions, while still disclosing that Project
  context may surface.
- Global instructions retain ownership of user-change protection, secrets,
  resources, long jobs, Git, external effects, and ask-first boundaries.
- `personal-brainstorms` and explicitly invoked `personal-grilling` own internal
  design shaping and decision-changing questions. Context, delegation,
  debugging, persistence, planning, explanation, and final verification remain
  with their specialist skills.
- No mechanical validator or reusable script is bundled. Profile validators,
  metadata checks, link checks, stale-protocol searches, and isolated behavior
  probes are more proportionate to this qualitative workflow.
- Memo write failure is a persistence failure, not evidence that the discussion
  result is false. Planning may reference the curated decision; no adjacent
  workflow may rewrite it.

```yaml
skill_admission:
  skill: personal-triad-discussion
  acquisition_mode: created
  source_classification: local-origin
  provenance_status: complete
  admission_status: admitted
  portability_disposition: internalized
  safety_status: passed
  safety_review: "static_pass: The instruction and Markdown-template surfaces were reviewed; user-mediated relay and bounded project memo writes do not grant implementation, resource launch, Git, publication, credential, or external-chat automation."
  trigger_status: passed
  trigger_review: "static_pass: Manual-only Triad invocation was reviewed against ordinary brainstorming, explicit grilling, direct GPT relay, worker evidence, and project decision documentation."
  validation_status: passed
  validation:
    - "static_pass: Local history, official product evidence, observed tool boundaries, metadata, links, and baseline behavior probes were reviewed on 2026-07-16."
    - "static_pass: The low-bandwidth role split, five-line opening, action labels, post-reply loop, delegation boundary, and separate Continuity Restart and Blank Restart contracts were reviewed in the active skill and packet reference."
    - "product_pass: A fresh post-GPT-reply smoke produced the five-line opening, one direct relay label, a compressed judgment, one complete relay, and no continue prompt on 2026-07-16."
    - "product_pass: A fresh Blank Restart smoke sent only the neutral new question, excluded the old memo, verified state, conclusion, and named consumer, and disclosed the Project-memory isolation limit on 2026-07-16."
  update_owner: "maintainer of personal-triad-discussion"
  update_rule: "Repeat provenance, safety, trigger, relay, memo, user-intervention, restart, and portability review before the source, interaction contract, persistence surface, or role boundaries change."
  rollback_basis: "Remove the skill through personal-skill-hygiene and restore the reviewed tree from codex-profile-kit revision 3791645f59c0eeec497755bd7301be78b44efbea."
  unknowns_disposition: bounded-nonmaterial
  unknowns:
    - "Direct Codex control of a user-owned GPT Pro Project chat was not available on the observed tool surface."
    - "The fresh CLI smokes followed the core SKILL contract but did not load the linked discussion-packets reference because their read-only tool path failed."
```
