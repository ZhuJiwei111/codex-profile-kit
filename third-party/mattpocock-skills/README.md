# Matt Pocock Skills

- Upstream: `https://github.com/mattpocock/skills`
- Version: `v1.2.3`
- Imported: 2026-08-08
- License: MIT; see [LICENSE](./LICENSE).

The portable profile vendors the 25 promoted skills listed by the upstream
`.claude-plugin/plugin.json` at this version. They are stored as independent
managed trees under `profile/skills/` so `profile_sync.py` can deploy them to
Codex without installing the upstream Claude plugin or the experimental
`in-progress` and `misc` buckets.

The imported skill trees are unmodified from upstream. Local profile rules,
including explicit authority for Git commits, external writes, credentials,
heavy work, and repository changes, continue to take precedence over workflow
steps suggested by a vendored skill.

Upstream user-invoked skills retain the Claude-oriented
`disable-model-invocation` frontmatter key, which Codex's strict
`quick_validate.py` does not accept. Their Codex policy is carried by the
co-located `agents/openai.yaml`; the repository contract test verifies that
every such skill sets `allow_implicit_invocation: false`.

To update them, review a new exact upstream tag, replace the complete promoted
set from that tag, update this version record and license if needed, then run
the repository contract tests and profile preview before committing.
