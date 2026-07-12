# Source Notes

Checked: 2026-07-12.

This skill is local-origin. Available Git history does not establish textual
derivation from an external skill. Current official Codex documentation is used
as product-behavior evidence; local authorization, host boundaries, secret
handling, and specialist workflow ownership take precedence. No external text
is copied into the skill, and no external derivative-license claim is made.

## Local History

- Initial profile-kit commit:
  `6574bce5f5ede8fb4566d0451ddcf613f7fdf8a5`
- Initial `SKILL.md` blob:
  `57a84b4228904652afeb0e0de595d706a6828ba2`
- Initial `agents/openai.yaml` blob:
  `099e8049fbff8f202cc4930d5c15a8abb115287b`

The initial version established useful manual-only, one-shot, read-only status
behavior. It also hard-coded a low/medium reasoning ceiling, exposed broad
process and raw-log examples, and mixed process liveness, progress, job success,
and task completion more than the current profile permits.

## Official Codex Evidence

The following current documentation was checked against local
`codex-cli 0.144.1` behavior:

- [Long-running work](https://learn.chatgpt.com/docs/long-running-work)
  documents status requests in the same task, status recap from a side task,
  native Goal controls, separate task context, and the rule that Goal does not
  broaden permissions.
- [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
  documents per-agent `model` and `model_reasoning_effort` configuration, the
  option to leave model selection unpinned, and the latency/cost tradeoff of
  higher reasoning effort.
- [Scheduled tasks](https://learn.chatgpt.com/docs/automations?surface=app)
  establishes the native product owner for recurring or background scheduled
  status work.
- [App Server](https://learn.chatgpt.com/docs/app-server) documents
  `config/mcpServer/reload`, `mcpServerStatus/list`, and thread-bound MCP tool
  calls.

Official pages are current documentation rather than commit-pinned source.
Recheck them and the local schema when auditing task, Goal, agent, automation,
or MCP behavior.

## MCP Reload Check

Before this revision, a temporary local stdio app-server using Codex 0.144.1
completed the initialize/initialized handshake, accepted
`config/mcpServer/reload` with null parameters, and returned the configured
OpenAI Docs MCP tools from `mcpServerStatus/list`. The check proved local MCP
configuration and reload behavior; it did not inject those tools into the
already-running Desktop task. A direct tool call through that temporary server
could not reuse the Desktop task because the thread was not loaded there.

No remote-control transport, trust state, daemon, or user configuration was
changed during that check.

## Adopted

- Keep this skill explicit and manual-only.
- Permit a same-task or observable parent-task status recap without making the
  status checker the task controller.
- Use one bounded read-only pass and return control immediately.
- Ground ETA in measurable external work or explicit bounded remaining steps.
- Keep recurring status in native Scheduled tasks or automation.
- Allow separately configured agents to use task-appropriate model and
  reasoning settings without assuming or changing the parent setting.

## Adapted

- Split process state, progress state, completion evidence, and final task
  verdict into separate owners and fields.
- Replace generic process discovery and raw log tails with exact-identity,
  metadata, count, manifest, and known-safe marker probes.
- Treat a side task with no observable parent evidence as `unknown` instead of
  reading private Codex task storage.
- Permit a conditional ETA with a confidence bound, while requiring `unknown`
  when the denominator, rate, identity, or comparable phase is absent.
- Route active monitoring to the local subagent and multiline contracts rather
  than interpreting product status recap as monitoring authority.

## Rejected

- A fixed low/medium ceiling for the already-running current or parent task.
- Prompt-only claims that a model or reasoning-effort switch took effect.
- System-wide process scans, full command arguments, raw log tails, or private
  task-store inspection to discover status.
- Treating process disappearance, session absence, stale output, or reached
  unit count as proof of task success.
- Automatic polling, repair, restart, verification, next-stage launch, Goal
  control, or scheduler emulation.
- ETA estimates for hidden model reasoning, elapsed silence, or generic task
  phases.

## Local Deviations

- Global `AGENTS.md` remains the owner of launch authorization, resources,
  startup guards, and long-job handoffs.
- `personal-subagent-boundaries` owns explicitly authorized monitoring agents;
  `personal-multiline-coordination` owns persistent visible worker lines.
- `personal-risk-verification` remains the only final completion gate, even
  when this skill observes a successful process exit or complete artifact set.
- No mechanical validator or generic status script is bundled. Status evidence
  is job-specific, and a generic scanner would encourage unsafe discovery and
  sensitive output.
- No live long job, active monitor, or Desktop side-task smoke test was launched
  for this revision.
