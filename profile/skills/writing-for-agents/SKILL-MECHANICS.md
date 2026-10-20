# Codex skill mechanics

Read this when authoring a Codex skill's metadata, invocation policy, or router.
Use the main [writing guide](SKILL.md) for the instruction body.

## Discovery and invocation

Keep `name` and `description` in `SKILL.md` frontmatter. The description states
the capability and conditions that should trigger it; keep detailed procedures
in the body or conditionally loaded references.

Codex permits implicit selection by default. Preserve an existing skill's
invocation policy unless the user requests a change. For an explicitly requested
manual-only skill, set this in `agents/openai.yaml`:

```yaml
policy:
  allow_implicit_invocation: false
```

Explicit `$skill-name` invocation remains available. The Claude-oriented
`disable-model-invocation` frontmatter key is not a substitute for Codex policy.
Do not infer script permissions, tool access, or mutation authority from either
invocation mode.

## Routers and shared material

A router should select the smallest useful workflow, then read its installed
entrypoint. Use the tools actually available in the host; a slash-style name in
prose does not register a native command or imply that a Skill tool exists.
Shared references may be plain files read by multiple skills. Do not create a
new discoverable skill merely to expose a shared definition or one generic rule.

Keep one coherent job per skill. Split when there is an independent user outcome
or a substantial conditional workflow, not just to reduce file length.

Source: [OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills).
