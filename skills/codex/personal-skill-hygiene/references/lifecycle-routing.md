# Lifecycle Routing

Choose the primary owner from the user's actual requested outcome. A named
artifact does not automatically make hygiene the owner.

| Requested outcome | Primary owner | Hygiene's role |
| --- | --- | --- |
| Audit one target's lifecycle state or decide whether to keep, disable, archive, restore, rename, remove, or replace it | `personal-skill-hygiene` | Own the evidence, disposition, rollback path, and approved state transition |
| Review one newly created or externally installed skill for admission, provenance, or portability | `personal-skill-hygiene` | Own the four admission dimensions, activation decision, update rule, and rollback evidence |
| Create or edit a skill's instructions, metadata, references, scripts, or assets | `skill-creator` | Require hygiene admission before activation or portable adoption; do not copy the system authoring workflow here |
| Discover a third-party skill | `find-skills` | Optionally assess lifecycle fit after candidates are known |
| Install a curated or GitHub-hosted skill | `skill-installer` | Review the exact candidate before activation; acquisition success is not admission |
| Create or update a plugin bundle or marketplace entry | `plugin-creator` | Decide whether an old plugin instance should be retained, disabled, archived, or replaced |
| Author, migrate, or test a Codex hook or controlled Markdown guard | `personal-codex-hook-rules` | Audit the lifecycle of a specific obsolete or duplicate hook only |
| Audit, compare, export, apply, or synchronize the whole reusable profile | `personal-codex-audit` | Accept a later handoff for one concrete lifecycle action |
| Configure or authenticate a standalone MCP server or connector | The product/MCP owner | Do not expand hygiene into auth or general MCP configuration |

## Mixed Requests

1. Identify the decision that must happen first.
2. If lifecycle disposition is unresolved, use hygiene to decide it before
   invoking the specialist implementation.
3. If the user already fixed the desired lifecycle disposition, route directly
   to the specialist. A newly created or installed skill still needs the
   admission contract before activation or portable adoption.
4. Keep authorization scoped: permission to audit or retire an old artifact is
   not permission to author, install, publish, or authenticate its replacement.
5. If no specialist is available, state the capability gap rather than silently
   broadening this skill.

## Boundary Examples

- "This old skill was replaced; should I keep it?" -> hygiene owns the
  lifecycle decision.
- "Rewrite this skill so it triggers less often" -> `skill-creator` owns the
  content change; hygiene owns the later admission decision when the change is
  for a new candidate.
- "Install this GitHub skill" -> hygiene reviews the exact candidate and
  `skill-installer` owns the approved acquisition mechanics.
- "Create a hook that blocks private-key edits" ->
  `personal-codex-hook-rules` owns hook authoring.
- "Audit all my skills and hooks, then export them" ->
  `personal-codex-audit` owns the profile-wide workflow.
- "Delete this plugin cache to uninstall the plugin" -> hygiene first verifies
  installed, enabled, source, and recovery state; cache deletion alone is not
  an uninstall decision.
