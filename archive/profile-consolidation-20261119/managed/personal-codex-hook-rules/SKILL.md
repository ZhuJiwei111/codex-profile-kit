---
name: personal-codex-hook-rules
description: Use when creating, editing, reviewing, testing, or migrating Codex native hooks, including event payloads, matchers, output JSON, runtime commands, and trust review.
---

# Personal Codex Hook Rules

Keep hooks as narrow mechanical guards. Put durable judgment in `AGENTS.md` and
conditional workflows in the owning skill.

## Work From The Active Protocol

1. Identify the installed Codex version, active hook source, event, canonical
   tool name, desired effect, and one matching and non-matching payload.
2. Read the current official documentation or the installed release schema for
   that version. Do not rely on copied protocol notes.
3. Inspect the applicable definition, handler, and focused tests. Preserve
   unrelated handlers and never edit persisted trust state.
4. Use `deny` only for a deterministic prohibition. Keep ordinary semantic
   advice out of executable guards.
5. Run a matching payload, non-matching payload, and an adjacent-tool or
   adjacent-rule case. Confirm stdout is empty or valid event-appropriate JSON;
   diagnostics belong on stderr.

Treat `PreToolUse` as a guardrail, not complete enforcement. Never include
secrets in definitions, fixtures, logs, or diagnostics.

## Change Definitions Safely

A changed unmanaged definition needs user review through `/hooks`. When
retiring a handler, first make the new definition and runner available. Use a
fresh task to review trust and dispatch before deleting a runner that the
current task may still have loaded. Do not add a permanent compatibility
wrapper for that transition.

Report the changed behavior, focused checks, trust state, and material matcher
or bypass risk.

Read `references/source-notes.md` only when updating provenance.
