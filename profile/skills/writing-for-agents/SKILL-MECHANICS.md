# Skill mechanics for Codex

Read this reference when writing a skill. Use [SKILL.md](SKILL.md) for document
structure and concise context pointers.

## Discovery and invocation

Every skill needs `name` and a concise `description` in SKILL.md frontmatter.
Describe its actual triggers and boundaries. Codex discovers metadata first,
loads the entrypoint when selected, then reads supporting files as needed.
Do not describe manual skills as having guaranteed zero context cost.

Set Codex invocation policy in `agents/openai.yaml`:

```yaml
policy:
  allow_implicit_invocation: false
```

The default is true. False prevents implicit selection based on the prompt;
explicit `$skill-name` invocation remains available. Use manual invocation for
workflows the user should deliberately select. Keep name, directory, description,
and default_prompt references consistent.

Imported Claude `disable-model-invocation` fields are historical compatibility
metadata, not the Codex invocation-policy owner. Preserve them only when an
upstream compatibility contract needs them; new Codex skills use native metadata.

## Shared references and routers

Invocation policy does not prohibit reading a known file. An authorized workflow
may reference another skill's instructions by a resolvable path, including a
manual skill. Reading it does not widen authority or independently activate an
unrequested workflow. Keep shared behavior in one owner and link to it.

A router selects the smallest workflow for the requested outcome. Read the
selected entrypoint, inherit task authority, and load supporting material only
when needed. Do not copy complete child procedures into the router.

Split skills when distinct user intents or independent discovery justify it;
use supporting references for details that have no separate invocation need.

## Validation

Check names, referenced paths, invocation metadata, and representative trigger
prompts. Use deterministic scripts only when the workflow needs deterministic
behavior. Local schema checks do not prove model selection or runtime loading.

Official reference: https://learn.chatgpt.com/docs/build-skills
Reviewed: 2026-09-05.
