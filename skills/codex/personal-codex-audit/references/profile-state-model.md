# Profile State Model

Use these labels consistently in collector output and audit reports.

## Evidence Labels

| Label | Meaning |
| --- | --- |
| `observed` | Directly read from an allowed current-host file or command result |
| `configured` | Present in an applicable configuration source |
| `user-reported` | Stated by the user but not independently confirmed in the current check |
| `product-confirmed` | Confirmed by the owning Codex UI or native product command |
| `not-collected` | Deliberately excluded by policy or collector design |
| `unknown` | Material evidence is missing, unsupported, or ambiguous |

Do not upgrade `user-reported`, `not-collected`, or `unknown` to `observed`.

## Component States

| State | Evidence required |
| --- | --- |
| `present` | The specific source, definition, file, or entry exists |
| `configured` | An owning config source references or controls the component |
| `global-feature-state` | An allowlisted feature flag or documented default applies |
| `individual-enabled` | The owning product confirms the individual component is enabled |
| `trusted` | The owning product confirms the current definition is trusted |
| `exported` | The expected portable counterpart exists in profile-kit |
| `verified` | Fresh validation passed after the last relevant change |

File presence never proves configuration, enablement, trust, export, or
verification.

## Hook State

Record hook evidence in separate fields:

- `definition_exists`: whether referenced local handler files can be safely
  resolved and observed.
- `configured`: whether `hooks.json` or an allowed inline hook source contains
  the handler registration.
- `global_feature_state`: `explicitly-enabled`, `explicitly-disabled`, or the
  documented default.
- `individual_enabled_state`: `not-collected` unless `/hooks` or equivalent
  product evidence confirms it.
- `trust_state`: `not-collected` unless `/hooks` confirms the current
  definition. Never inspect or compare a persisted trust hash.

A configured hook with an existing script may still be disabled or awaiting
trust. A trusted definition may become untrusted after any definition change.

## Skill State

- A discovered skill entry may be a normal directory or a symlink.
- `skills.config` can explicitly enable or disable a referenced skill.
- Metadata presence does not prove implicit invocation or behavioral quality.
- For outside-home or sensitive symlink targets, report the entry but leave
  metadata `not-read`.

## MCP State

- A projected MCP entry proves only that a declaration was parsed from the
  current config source.
- `enabled` is the declared config boolean, not product-confirmed liveness or
  successful initialization. `null` means the declaration omitted the field.
- `transport` is derived only from the presence of `url` or `command`; raw
  commands and arguments remain excluded.
- `public_url` is an allowlisted public endpoint identity. Its absence may mean
  the URL was local, non-HTTPS, auth-bearing, malformed, or deliberately
  withheld; it does not mean that no URL was configured.
- `auth_mechanism` describes only the configuration category. It never proves
  that credentials exist, OAuth completed, headers are correct, or a server is
  currently usable.
- Runtime health, available tools, login state, and OAuth state remain
  `not-collected` unless a separately authorized product check supplies safe
  evidence.

## Profile-Kit State

- `only_export`, `only_repo`, and `different` are drift categories, not an
  instruction to overwrite one side.
- Export uses active portable assets as source; apply uses the reviewed kit as
  source.
- `verify` proves only the checks it ran. It does not prove hook trust, external
  publication, connector or MCP authorization, MCP runtime health, or
  cross-host equality.

## Reporting Rule

For every consequential claim, include the component, state, evidence label,
evidence source, and any remaining user-controlled or product-controlled step.
