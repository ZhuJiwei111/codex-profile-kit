# Codex Compatibility Policy

Use this policy when the installed Codex version or a relevant product contract
changed after the last supported profile verification.

## Baseline

- Verified baseline: `codex-cli 0.144.1`.
- The baseline records the contracts that were actually exercised. It is not a
  requirement that every later verification use exactly the same version.
- Record the current version and the relevant release-note or schema evidence
  before deciding how much to rerun.

## Choose Revalidation By Contract

| Change | Minimum response |
| --- | --- |
| Patch update with no relevant documented or observed contract change | Run the cheap loader/schema smoke and affected focused tests |
| Patch update touching a relevant surface | Revalidate that surface and its nearest consumers |
| Minor or major update | Review release notes and run every affected surface suite; use a full profile audit when several surfaces changed |
| Focused smoke failure or unexplained behavioral drift | Stop the compatibility claim and broaden to the owning surface audit |
| Direct schema or discovery change at any version | Revalidate the affected contract regardless of semantic-version size |

Do not skip all checks because an update is labelled “small,” and do not run a
full audit merely because the version string differs from `0.144.1`.

## Surface Triggers

| Surface | Trigger examples | Focused evidence |
| --- | --- | --- |
| Native hooks | Event list, matcher, input/output schema, tool names, trust behavior | Hook schema fixtures and real-shape payload tests |
| Custom agents | Agent TOML, model/reasoning fields, sandbox inheritance, loader or spawn behavior | Custom-agent loader/schema smoke and affected routing probe |
| Skill discovery | Discovery roots, `openai.yaml`, invocation policy, catalog budget, rename behavior | Validators, catalog/discovery smoke, positive and negative route probes |
| Config and MCP | MCP field ownership, transport/auth configuration, config layering | Collector parser tests, secret-negative tests, safe declaration comparison |
| Profile transfer | Manifest, export/apply targets, backup behavior, generated templates | Sync tests, dry run, `verify`, and drift audit |

If one surface passes and another was not exercised, report the result as
surface-specific rather than whole-profile compatibility.

## Full-Audit Triggers

Run the whole-profile audit when any of these holds:

- a minor or major update changes several owned surfaces;
- release notes announce a breaking configuration, discovery, hook, agent, or
  transfer change;
- focused checks fail in more than one surface;
- the active profile or profile-kit migration model changed broadly;
- the requested claim is whole-profile compatibility rather than a focused
  component check.

## Documentation Source Failure Reuse

Within one task, reuse a confirmed deterministic helper or endpoint failure and
the approved official fallback. Do not repeat an unchanged request merely for
ceremony. A later bounded retry is appropriate only when the helper version,
endpoint, network state, task, or required documentation claim materially
changed. Dated HTTP 403 evidence does not permanently disable the official
manual helper.
