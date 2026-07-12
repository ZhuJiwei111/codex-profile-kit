# Profile Source Policy

Use this policy before collecting or summarizing the current host's reusable
Codex profile.

## Contents

- Scope and default sources
- MCP safe projection
- Memory and symlink boundaries
- Default exclusions and reporting

## Scope

- Keep the audit on the current execution host. A different home path is not
  evidence of a different host's authorization.
- Limit the default inventory to durable profile assets. Tasks, threads,
  sessions, transcripts, runtime databases, and app-wide history are out of
  scope.
- Subagents inherit the same host and source boundary.

## Default Sources

Read only the smallest safe projection needed from these sources when present:

| Source | Allowed projection |
| --- | --- |
| `~/.codex/AGENTS.md` | Existence, headings, and relevant durable rules |
| `~/.codex/skills/*/SKILL.md` | Personal/custom skill name, description, path, and safe resource structure |
| `~/.agents/skills/*/SKILL.md` | User/agent skill name, description, path, and safe resource structure |
| `agents/openai.yaml` | Presence and UI metadata needed for a requested skill audit |
| `~/.codex/config.toml` | Allowlisted feature booleans, `skills.config` path/enablement fields, and the safe MCP projection below |
| `~/.codex/hooks.json` or inline `[hooks]` | Event, matcher presence/length, handler type, and referenced file state; never raw command text |
| Referenced files under `~/.codex/hooks/` | Existence and a short module-doc or heading summary |
| `~/.codex/hookify/*.md` | Top-level safe frontmatter only; never nested or raw regex content by default |
| `~/codex-profile-kit` | Git state, safe dry-run diff, manifest, and exported portable assets when comparison is requested |

Read `~/.codex/HOST_LOCAL.md` only when resolving current-host profile paths or
environment facts is material. Do not export the populated host overlay.

## MCP Projection

For each configured `mcp_servers.<id>` entry, collect only:

- a syntactically safe server id;
- the declared `enabled` boolean, or `null` when unspecified;
- transport category: `streamable-http`, `stdio`, or `unknown`;
- `public_url` only for an explicitly reviewed allowlisted public HTTPS URL
  without userinfo, query, fragment, control characters, whitespace, or a
  local/private host;
- one auth mechanism category: `none`, `env-var-name`, `headers`,
  `oauth-or-runtime`, or `not-collected`.

Do not serialize MCP `command`, `args`, environment entries, bearer-token
variable names or values, header names or values, OAuth material, runtime
health, login state, or tool results. A declared public URL does not prove
reachability, authentication, availability, or successful initialization.

## Memory Is Explicit Opt-In

- The collector may report the safe `[features].memories` state, but it never
  reads memory content.
- Do not read `~/.codex/memories/` during an ordinary profile audit.
- Use memory only when the user explicitly requests a memory-informed audit and
  the current task's memory controls permit it.
- Then inspect only the minimum current-host entries needed for reusable Codex
  workflow preferences. Exclude project outcomes, experiment logs, remote-host
  state, papers, data transfers, and one-off troubleshooting.
- Label all retained findings `memory-derived` and possibly stale. Never copy
  memory content into profile-kit without a separately approved migration
  design.

## Symlink Boundary

- Inventory a symlinked skill entry because Codex may discover it.
- Read target metadata only when the resolved `SKILL.md` remains under the
  current home and avoids excluded or sensitive paths.
- For outside-home, sensitive, or broken targets, report the entry and
  `metadata_status` without reading target content.

## Default Exclusions

Never read, serialize, or summarize by default:

- Credentials, tokens, cookies, private keys, `.netrc`, authenticated URLs, or
  secret environment files.
- `auth.json`, `history.jsonl`, `session_index.jsonl`, SQLite/WAL/SHM files,
  attachments, logs, caches, plugin caches, or raw transcripts.
- Hook trust hashes, individual hook approval state, project trust, connector
  OAuth state, plugin runtime state, or approval history.
- MCP command lines, arguments, environment entries, bearer-token fields,
  header material, OAuth state, runtime health, or tool output.
- Other-host tasks, threads, memories, previews, messages, or session-derived
  summaries.
- Long generated artifacts, archived sessions, or unrelated project files.

If a requested conclusion depends on an excluded source, report the limitation.
Do not turn permission to audit into permission to inspect credentials or
high-noise runtime state.

## Reporting Boundary

- Distinguish observed files, parsed configuration, user reports, product UI
  confirmation, and unknown state.
- Prefer paths relative to the current home. For outside-home symlink or command
  targets, report only the category and basename needed to explain the gap.
- Do not print raw hook commands, raw matcher patterns, full config files, or
  memory extracts. Do not print raw MCP definitions; use only the safe
  schema-v3 projection.
- Separate observations from recommended changes and state the exact authority
  needed for each write.
