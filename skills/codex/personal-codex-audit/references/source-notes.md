# Source Notes

Checked: 2026-07-14.

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
  legacy `push` parser remains only for fail-closed compatibility: it exits
  before export, status inspection, staging, commit, or push and routes the
  supported publication workflow to `github:yeet`.
- Current-host workflow evidence on 2026-07-14 separated routine execution cost
  from orchestration delay: the documented network path completed fetch in
  seconds, while repeated transport fallbacks, duplicated verification,
  Git-state surprises, and per-stage authorization round trips dominated
  elapsed time.
- The user-approved directional fast path treats an explicit sync-to-GitHub or
  sync-from-GitHub outcome as authority for its bounded ordinary chain. The
  outbound chain ends with a verified candidate handoff to `github:yeet`, which
  exclusively owns branch setup, commit, push, and draft pull-request creation.
  It retains escalation gates for new assets, broad policy surfaces, conflicts,
  visibility changes, credentials, compatibility, and sensitive state.
- The user-approved 2026-07-14 admission design keeps `.system/skill-creator`
  and `.system/skill-installer` product-owned while adding local provenance,
  safety, trigger, portability, update, and rollback gates through
  `personal-skill-hygiene`.
- `THIRD_PARTY_SKILLS.lock.json` is the portable vendor lock. It binds the
  explicit allowlist to a complete tree digest and records unresolved source
  evidence rather than promoting a local snapshot to an upstream commit.

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
- Treating a bare export as authorization to stage, commit, push, publish, or
  change repository visibility. Explicit bounded outbound-sync intent is
  separately defined and still never authorizes a visibility change.
- Treating successful creation, installation, discovery, enablement, or export
  as a skill-admission verdict.
- Copying product-owned system skills into profile-kit to enforce local policy.

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
- Whole-profile audit aggregates admission state; it does not decide or mutate
  one candidate's admission. That remains owned by `personal-skill-hygiene`.
- Outbound publication handoffs carry
  `dependency_install_authorized: false`. Network or proxy evidence selects a
  path only; it does not grant publication, credential, installation, launch,
  or verdict authority. The cached `github:yeet` source remains external and is
  not modified by this profile skill.

```yaml
skill_admission:
  skill: personal-codex-audit
  acquisition_mode: created
  source_classification: hybrid
  provenance_status: complete
  admission_status: admitted
  portability_disposition: internalized
  safety_status: passed
  safety_review: "static_pass: The bundled collector and tests were inspected as a bounded non-secret profile projection; collection does not grant apply, Git, publication, credential, or dependency-install authority."
  trigger_status: passed
  trigger_review: "static_pass: Whole-profile audit and directional transfer ownership was reviewed against targeted skill hygiene, hook authoring, ordinary status, and github:yeet publication."
  validation_status: passed
  validation:
    - "static_pass: Official live sources, local compatibility evidence, collector boundaries, and portable lock design reviewed on 2026-07-16."
    - "static_pass: Targeted personal-skill admission validator fixtures passed on 2026-07-16."
  update_owner: "maintainer of personal-codex-audit"
  update_rule: "Repeat provenance, safety, trigger, executable-surface, and portability review before collector, source, trigger, transfer, or ownership changes enter portable export."
  rollback_basis: "Remove the skill through personal-skill-hygiene and restore the reviewed tree from codex-profile-kit revision 3791645f59c0eeec497755bd7301be78b44efbea."
  unknowns_disposition: none
  unknowns: []
```
