# Source Notes

Checked: 2026-07-12.

This skill applies official Codex documentation to the local profile design.
It does not copy external implementation code.

## Official Sources

| Source | Status | Adopted evidence |
| --- | --- | --- |
| [Customization overview](https://learn.chatgpt.com/docs/customization/overview) | Live OpenAI documentation checked 2026-07-11 | `AGENTS.md`, memories, skills, MCP, and subagents are complementary surfaces with different ownership |
| [Build skills](https://learn.chatgpt.com/docs/build-skills) | Live OpenAI documentation checked 2026-07-11 | Progressive disclosure, concise trigger descriptions, `skills.config`, and symlinked skill discovery |
| [Hooks](https://learn.chatgpt.com/docs/hooks) | Live OpenAI documentation checked 2026-07-11 | Hook discovery sources, default enablement, definition-hash trust, `/hooks` review, and configuration layering |
| [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) | Live OpenAI documentation checked 2026-07-12 | `skills.config`, feature flags, MCP declaration fields, and configuration ownership |
| [Memories](https://learn.chatgpt.com/docs/customization/memories) | Live OpenAI documentation checked 2026-07-11 | Local memories are generated state, off by default, task-controllable, and separate from durable required guidance |

Observed 2026-07-11: the Codex manual helper's `HEAD` request returned HTTP 403
during broad Codex self-knowledge lookup. The official Docs MCP and pages above
were used as the bounded same-task fallback. This is dated evidence, not a
permanent helper ban; retry only when the helper version, endpoint, network
state, task, or required claim materially changes.

## Local Evidence

- Current host Codex CLI at audit time: `0.144.1`.
- `0.144.1` is the current verified compatibility baseline, not an exact-version
  gate. See `compatibility-policy.md` for patch, surface, and full-audit triggers.
- Current host Python: `3.10.12`; `tomllib` and `tomli` were unavailable.
- The collector therefore provides a dependency-free limited TOML projection
  on Python 3.10 and uses `tomllib` when available.
- Collector schema v3 adds a safe MCP declaration inventory. It emits only id,
  declared enablement, transport category, an explicitly reviewed allowlisted
  public HTTPS endpoint for an unauthenticated declaration, and an auth
  mechanism category.
- Current-session behavior confirms personal skills under
  `~/.codex/skills/`; public documentation also identifies
  `$HOME/.agents/skills` as a user skill root.
- `codex-profile-kit/scripts/sync.py` is the local transfer mechanism. Its
  `push --confirm` path stages with `git add -A`, so this skill adds a clean-diff
  authorization gate without modifying the sync script.

## Deliberately Rejected

- Treating every file under `~/.codex/hooks/` as a configured native hook.
- Inferring individual enablement or trust from file presence, registration,
  the global feature flag, or a remembered trust result.
- Reading or comparing persisted hook trust hashes.
- Serializing MCP commands, arguments, environment entries, bearer-token
  fields, headers, OAuth state, runtime health, or tool output.
- Reading local memory content during every profile audit merely because the
  memory feature is enabled.
- Enumerating tasks, threads, sessions, or other-host state as reusable profile
  inventory.
- Treating export as authorization to stage, commit, push, publish, or change
  repository visibility.

## Local Deviations

- The collector inventories only the current user's safe profile projection;
  managed and plugin-bundled hook runtime states remain `not-collected`.
- Raw hook commands and matcher patterns are intentionally omitted even though
  the local files contain them.
- MCP authentication and runtime data are reduced to a non-secret mechanism
  category; the collector does not claim that a configured server is usable.
- Outside-home symlink targets are listed but not followed.
- Memory-informed audits remain possible only after explicit user opt-in and do
  not make memory part of the ordinary portable snapshot.
