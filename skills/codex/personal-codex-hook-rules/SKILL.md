---
name: personal-codex-hook-rules
description: Use when creating, editing, reviewing, testing, or migrating Codex native hooks, including event payloads, matchers, output JSON, and trust review.
---

# Personal Codex Hook Rules

Create focused mechanical guards for Codex. Keep durable behavior in AGENTS.md
and conditional semantic workflows in skills rather than encoding them as hooks.

## Scope

- Treat explanation, review, and diagnosis requests as read-only unless the user
  also authorizes a change.
- A hook change needs authority to edit the applicable user or project
  configuration; a read-only audit does not grant it.
- Inspect the installed Codex version and active hook source before relying on an
  event or output field.
- Use hooks for focused mechanical checks. Put behavior and judgment in
  AGENTS.md or the owning skill, and whole-profile movement in
  `personal-codex-audit`.
- Keep one owner for each rule; do not duplicate the same enforcement in a hook
  and a semantic workflow.

## Workflow

1. Define the scope, event, canonical tool name, desired effect, and one positive
   and one negative example. Use `deny` only for deterministic prohibitions;
   represent ordinary ask-first guidance as model-visible context.
2. Inspect the applicable `hooks.json` or `config.toml`, handler, tests, and
   existing rules. Check `codex --version` when protocol details matter.
3. Read [native-hooks.md](references/native-hooks.md) for discovery, trust,
   matchers, payloads, and outputs, and [testing.md](references/testing.md) for
   every behavior change. Read [source-notes.md](references/source-notes.md)
   only when refreshing provenance or the official baseline.
4. Add or identify the smallest failing payload test when a harness exists. For
   documentation-only changes, use exact path, field, and command consistency
   checks instead.
5. Make the smallest authorized edit. Preserve unrelated rules and user changes;
   never stage, commit, push, or alter persisted trust hashes implicitly.
6. Run a matching payload, a non-matching payload, and an adjacent-rule conflict
   case. Confirm stdout is valid event-appropriate JSON or empty, and keep
   diagnostics on stderr.
7. If a hook definition changed, report that it is untrusted until the user
   reviews it through `/hooks`.
8. Report files changed, behavior covered, exact checks, trust status, untested
   paths, and any remaining bypass or matcher risk.

## Hard Boundaries

- Do not create catch-all Stop reminders, writing-style hooks, discussion hooks,
  automatic Git staging, or generic completion checklists.
- Do not treat `PreToolUse` as a complete enforcement boundary; equivalent work
  may remain possible through an uncovered tool path.
- Never include secret values in rules, fixtures, logs, diagnostics, or reports.
- Do not edit credential-bearing files or use hooks to bypass an approval model.
