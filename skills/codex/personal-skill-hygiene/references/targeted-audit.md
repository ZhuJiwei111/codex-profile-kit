# Targeted Lifecycle Audit

Use this reference for one concrete artifact or a tightly related old/new pair.
Do not turn it into a broad profile inventory.

## State Model

Record each state as `yes`, `no`, `unknown`, or `not-applicable`, with its
evidence source.

| State | Meaning | Do not infer it from |
| --- | --- | --- |
| `exists` | A source, installed copy, definition, or archive is present | A stale registry entry or remembered installation |
| `discoverable/registered` | Codex can discover the skill, or the plugin/hook is registered by its owning mechanism | Mere file existence |
| `configured` | A relevant configuration entry points at or controls the target | Cache contents |
| `enabled` | The owning mechanism currently permits use | Configuration presence without its effective value |
| `trusted` | The user-facing trust flow currently accepts a hook definition | Registration, enablement, or a locally edited hash |
| `cached` | A derived or downloaded copy exists | Installation, enablement, ownership, or uniqueness |
| `archived` | A recovery copy exists outside active discovery and its path is known | An unverified backup label |

Trust is user-controlled. Report `unknown` when the product does not expose
trust state safely; ask the user to verify it through the native trust UI rather
than reading or editing a trust hash.

## Artifact-Specific Evidence

### Skill

- Confirm the active path, folder/frontmatter name match, description, and any
  `agents/openai.yaml` metadata.
- Check whether the path is within a discovered skill root and whether an
  explicit configuration disables it.
- Resolve local resource links before calling the copy healthy.
- Identify an independent source or archive before rename, replacement, or
  removal.

### Plugin

- Separate source checkout, marketplace entry, installed copy, cache, and
  staging directory.
- Inspect the official plugin manifest/configuration mechanism that owns
  installation and enablement. Do not use cache presence or size as its proxy.
- Establish whether cached material is reproducible from a verified source and
  whether it contains the only local modifications before cleanup.

### Hook

- Separate definition files, hook registration, effective enablement, and
  user trust.
- Validate with the native hook workflow or the owning hook skill. Definition
  edits may require the user to review and trust them again.
- Never edit a stored trust hash or claim trust from file equality alone.

### MCP or Connector

Only inspect lifecycle facts when the MCP server is bundled with the target
skill or plugin. Route standalone configuration and authentication to the
product/MCP owner. Never expose tokens, cookies, authenticated URLs, or client
secrets.

## Dispositions

| Disposition | Use when |
| --- | --- |
| `keep` | The target has a distinct owner and remains useful and healthy |
| `update-via-specialist` | The lifecycle is valid but content or implementation needs specialist work |
| `disable` | Use should stop while recovery and evidence remain intact |
| `archive` | Active discovery should stop but a recoverable copy is still needed |
| `restore` | A verified archive or source should become active again |
| `rename` | Identity must change and every active reference can be updated atomically |
| `remove` | Use has stopped, recovery is independently verified or intentionally waived, and no live references remain |
| `replace` | A verified successor covers the accepted responsibilities and rollback remains available until validation passes |
| `needs-clarification` | Ownership, desired behavior, evidence, or authorization would materially change the action |

Use `needs-clarification` instead of a mutating disposition whenever that
disposition's required state is still unknown. Report a likely later action as
a conditional recommendation, not as the current disposition.

## Recoverable Transition

Use the relevant subset of this order:

1. Stop new use through the official disable mechanism.
2. Preserve a non-discoverable archive with an exact path and provenance.
3. Install or activate the replacement through its specialist workflow.
4. Verify the replacement's trigger, resources, behavior, and ownership.
5. Remove obsolete registrations or active copies.
6. Clean derived caches only after reconstructibility and absence of unique
   local changes are established.
7. Re-check the final state and retained rollback path.

Do not perform all stages automatically. Each stage must be inside the user's
authorized outcome, and a later stage may require separate authority.

## Minimal Report

- `Target`: exact name and path or registry identity.
- `Observed states`: state values with evidence; label unknowns.
- `Disposition`: one outcome and why it fits.
- `Action`: actual mutation, or `none` for a read-only audit.
- `Recovery`: archive/source path and the restore mechanism.
- `Validation`: command or native UI check and observed result.
- `Residual risk`: unverified trust, external source, stale reference, or
  user-controlled step.
