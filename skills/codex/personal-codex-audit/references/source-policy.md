# Source Policy

Use this policy before collecting or summarizing the user's Codex profile.

## Default Sources

Read these sources by default when they exist:

- `~/.codex/AGENTS.md`: durable server-level Codex behavior preferences.
- `~/.codex/skills/*/SKILL.md`: personal/custom Codex skill names, descriptions, and concise workflow intent.
- `~/.agents/skills/*/SKILL.md`: legacy or agent-level skills, especially `find-skills`.
- `~/.codex/hookify/*.md`: safe Hookify rule frontmatter fields and short rule descriptions; avoid printing raw regex patterns unless the user asks for rule debugging.
- `~/.codex/hooks`: native hook filenames and safe metadata such as Markdown frontmatter or a short module docstring.
- `~/.codex/memories/MEMORY.md`: only reusable cross-task Codex workflow preferences and lessons.

Prefer current files for current state. Use memory only as a reusable signal or historical explanation.

## Default Exclusions

Do not read or summarize these by default:

- Auth, credential, token, cookie, password, SSH key, `.netrc`, secret, or Codex auth files.
- `auth.json`, `history.jsonl`, `session_index.jsonl`, SQLite files, attachments, caches, plugin caches, logs, and raw session transcripts.
- Project-specific or task-specific memories, including experiment logs, paper/rebuttal state, remote server state, dataset transfer records, platform-specific setup, and one-off troubleshooting.
- Long logs, generated artifacts, archived sessions, or high-noise historical dumps.

If the user explicitly requests one of these sources, ask before reading anything sensitive and report only redacted configuration categories.

## Memory Filtering

When searching memory, keep only signals that are portable across future Codex sessions, such as:

- Stable user preferences for asking questions, language, evidence boundaries, long-running jobs, temporary work, or safe configuration changes.
- Stable mappings of where reusable Codex assets live.
- Lessons about maintaining skills, hooks, AGENTS rules, migration kits, or workflow portability.

Exclude memories whose main value is tied to a particular repository, experiment, machine, remote host, paper, data transfer, CI run, or old task outcome.

## Reporting Boundaries

In the final user-facing report:

- Write in Chinese by default.
- Distinguish observed current files from memory-derived context.
- Mention stale or missing evidence instead of filling gaps with assumptions.
- Put actual edits under `需要你批准的建议`; do not make them during this audit.
