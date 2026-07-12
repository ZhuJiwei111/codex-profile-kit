---
name: personal-codex-hook-rules
description: Use when creating, editing, reviewing, testing, or migrating Codex native hooks or controlled global Markdown guards, including PreToolUse JSON and trust review.
---

# Personal Codex Hook Rules

Create focused mechanical guards for Codex. Keep durable behavior in AGENTS.md
and conditional semantic workflows in skills rather than encoding them as hooks.

## Contract

- Treat explanation, review, and diagnosis requests as read-only unless the user
  also authorizes a change.
- Before editing user-level or project-level hook configuration, confirm that the
  requested outcome authorizes that configuration change.
- Inspect the installed Codex version and active hook source before relying on an
  event or output field. Do not assume Claude Hookify compatibility.
- Keep one owner for each rule. Do not duplicate the same policy across native
  hooks, the Markdown adapter, AGENTS.md, and a workflow skill.

## Choose The Mechanism

| Need | Mechanism |
| --- | --- |
| Simple global Bash or `apply_patch` pattern | Controlled global Markdown adapter |
| Project policy, MCP tool, another event, or complex logic | Codex native hook |
| Discussion posture, writing style, completion discipline, or workflow | AGENTS.md or the owning skill |
| Whole-profile audit, migration, installation, enablement, or archival | `personal-codex-audit` or `personal-skill-hygiene` |

Use the Markdown adapter only when its deliberately small language expresses the
rule without ambiguity. Otherwise use a native hook rather than extending the
adapter casually.

## Workflow

1. Define the scope, event, canonical tool name, desired effect, and one positive
   and one negative example. Use `deny` only for deterministic prohibitions;
   represent ordinary ask-first guidance as model-visible context.
2. Inspect the applicable `hooks.json` or `config.toml`, handler, tests, and
   existing rules. Check `codex --version` when protocol details matter.
3. Read the matching reference:
   - Read [native-hooks.md](references/native-hooks.md) for native discovery,
     trust, matcher, payload, or output work.
   - Read [markdown-adapter.md](references/markdown-adapter.md) before creating or
     changing a controlled global Markdown rule.
   - Read [testing.md](references/testing.md) for every behavior change.
   - Read [source-notes.md](references/source-notes.md) only for provenance,
     upstream comparison, or baseline refreshes.
4. Add or identify the smallest failing payload test when a harness exists. For
   documentation-only changes, use exact path, field, and command consistency
   checks instead.
5. Make the smallest authorized edit. Preserve unrelated rules and user changes;
   never stage, commit, push, or alter persisted trust hashes implicitly.
6. Run a matching payload, a non-matching payload, and an adjacent-rule conflict
   case. Confirm stdout is valid event-appropriate JSON or empty, and keep
   diagnostics on stderr.
7. If a hook definition changed, report that it is untrusted until the user
   reviews it through `/hooks`. A Markdown rule-body change does not by itself
   justify editing trust state.
8. Report files changed, behavior covered, exact checks, trust status, untested
   paths, and any remaining bypass or matcher risk.

## Hard Boundaries

- The controlled Markdown adapter supports only `bash` and `file` rules with
  `warn` or `block`; it does not support `stop`, `prompt`, or `all`.
- Load Markdown adapter rules only from the controlled global directory. Project
  hooks must use Codex native discovery and trust.
- Do not create catch-all Stop reminders, writing-style hooks, discussion hooks,
  automatic Git staging, or generic completion checklists.
- Do not treat `PreToolUse` as a complete enforcement boundary; equivalent work
  may remain possible through an uncovered tool path.
- Never include secret values in rules, fixtures, logs, diagnostics, or reports.
- Do not edit credential-bearing files or use hooks to bypass an approval model.
