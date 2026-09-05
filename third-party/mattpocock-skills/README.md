# Matt Pocock Skills

- Upstream: `https://github.com/mattpocock/skills`
- Version: `v1.2.3`
- Imported: 2026-08-08
- License: MIT; see [LICENSE](./LICENSE).

The original import contained the 25 promoted skills listed by the upstream
`.claude-plugin/plugin.json` at this version. They are stored as independent
managed trees under `profile/skills/` so `profile_sync.py` can deploy them to
Codex without installing the upstream Claude plugin or the experimental
`in-progress` and `misc` buckets.

The imported skill trees retain the upstream content except for these reviewed
local adaptations:

- `diagnosing-bugs/SKILL.md`: complex-failure routing, evidence-led phase
  selection, bounded probes, and proportionate verification replace mandatory
  phase gates and fixed hypothesis or repetition counts.
- `code-review/SKILL.md`: select uncommitted, commit, branch, or PR scope;
  include relevant untracked files, allow review without tracker setup, use
  delegation only with authority, and let the main agent synthesize findings.
- `research`, `prototype`, `domain-modeling`, and `wizard` entrypoints: align
  file output, production edits, delegation, credentials, Git, and external
  actions with the user's actual authority instead of automatic workflow steps.
- Upstream `grilling`, `grill-me`, and `grill-with-docs` are retired in favor
  of explicit-only `personal-grilling` (questioning core) and
  `personal-grill-with-docs` (documentation and continuity). Dependent callers
  in `ask-matt`, `triage`, `wayfinder`, `improve-codebase-architecture`, and
  setup domain guidance route to the new pair within existing authority.
- `ask-matt`: route to current child entrypoints without restoring retired
  reproduction gates, automatic prototype integration or Git writes, mandatory
  handoffs, or tracker setup for workflows that do not need it.

Preserve these adaptations when reviewing an upstream update. Local profile rules,
including explicit authority for Git commits, external writes, credentials,
heavy work, and repository changes, continue to take precedence over workflow
steps suggested by a vendored skill.

Upstream user-invoked skills retain the Claude-oriented
`disable-model-invocation` frontmatter key, which Codex's strict
`quick_validate.py` does not accept. Their Codex policy is carried by the
co-located `agents/openai.yaml`; the repository contract test verifies that
every such skill sets `allow_implicit_invocation: false`.

To update them, review a new exact upstream tag, reconcile the promoted
set from that tag with these local adaptations and retirements, update this version record and license if needed, then run
the repository contract tests and profile preview before committing.
