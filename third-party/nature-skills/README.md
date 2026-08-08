# Nature Skills

- Upstream: `https://github.com/yuan1z0825/nature-skills`
- Revision: `703c150ec6b3d7885dc93aa0232a6b7fdd6686ed`
- Imported: 2026-08-08
- License: Apache-2.0; see [LICENSE](./LICENSE). Individual imported trees may
  retain additional bundled license notices.

The portable profile vendors the 18 `nature-*` child skills installed from this
revision plus upstream `nature-proposal-writer`, which is installed under
`profile/skills/researchwrite/` to match its `name: researchwrite` frontmatter.
The local `$nature` router is maintained separately under
`profile/skills/nature/`.

The imported snapshot was matched against the local installation using every
skill's Git tree hash recorded in `~/.agents/.skill-lock.json`. Local
post-install integration changes are retained: six skill frontmatters normalize
version and author fields under `metadata`, and every child has Codex
`agents/openai.yaml` metadata with `allow_implicit_invocation: false`. Portable
profile contract metadata adds missing display names and short descriptions.

The child skills include executable Python, MJS, and shell helpers. Some routes
can access literature services, institution-authorized browser sessions,
credential configuration, OpenRouter image generation, or recurring delivery.
They remain explicit-only, and the portable profile's authority, credential,
networking, external-write, and persistent-job rules take precedence.

To update the snapshot, inspect a new exact upstream revision, compare it with
the retained local integration changes, replace the complete imported trees,
reapply only reviewed integration metadata, update this record and license if
needed, then run the repository contract tests and profile preview.
