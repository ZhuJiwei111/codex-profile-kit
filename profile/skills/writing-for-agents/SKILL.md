---
name: writing-for-agents
description: Write or revise skills and agent-facing instructions when their wording, scope, or loading conditions affect behavior.
---

# Writing for Agents

Write instructions that change the agent's decisions for the requested task.
For Codex skill metadata and invocation, read [SKILL-MECHANICS.md](SKILL-MECHANICS.md).

## Scope and authority

Preserve user intent, existing owners, and authorization boundaries. Distinguish
an instruction from an example, a host fact, a task state, and a policy. Put each
in its actual owner rather than copying all of them into a skill or AGENTS.md.
A past incident should become a general rule only when a real recurring path
justifies it.

## Routing and structure

Keep descriptions short and specific to the workflow. State the capability and
trigger conditions before detailed procedure. Avoid synonyms that add no new
case, generic catchalls, and claims that the skill is universally required.

Keep essential actions and non-obvious constraints in the entrypoint. Move a
substantial conditional branch to a linked reference and state when to read it.
Use one authoritative definition for shared material; do not create a new skill
or a deep chain of routers just to expose it.

Use the host's available tools and actual project conventions. Prefer looking
up cheap environment facts to embedding copies that can become stale.

## Procedure and completion

State the desired action, meaningful decision boundary, and observable result.
Match control to risk: fragile operations need precise order; ordinary work
needs room for judgment. Preserve real user choices without adding repeated
confirmation, fixed stage counts, mandatory files, or exhaustive questionnaires.

Use familiar language and concrete examples. Keep a prohibition when it protects
an actual boundary; pair it with the correct action. Avoid unsupported claims
about prompt psychology, model-specific context thresholds, or magic keywords.

## Check

Remove repeated rules, generic advice, obsolete tools, and process that adds no
value. Review realistic positive and adjacent negative requests against the
trigger, follow the important branches, and validate the resulting metadata or
changed helper. Use live behavioral evaluation when its cost and risk are
warranted; a schema check alone does not establish model effectiveness.
