# Remote Connection Contract — Portable Example

This is a reviewed, static, manual-only schema. Copy it outside the profile
repository before filling it. Never commit host values or credential material.
Unresolved placeholders are not executable. Profile export regenerates this
example from `scripts/sync.py`; export, audit, verify, and apply never read,
copy, create, overwrite, back up, or delete the active connection contract.

## Scope And Ownership

- Scope: current execution host only
- Control-plane owner: `{{CONTROL_PLANE_OWNER_ROLE}}`
- Runtime owner: `{{RUNTIME_OWNER_ROLE}}`
- Change authority: `{{EXPLICIT_USER_CONTROLLED_WORKFLOW}}`
- Active contract location: `{{HOST_LOCAL_CONTRACT_LOCATION}}`
- Required access mode: `{{RESTRICTIVE_LOCAL_ACCESS_MODE}}`

Record ownership boundaries before any transport, proxy, launcher, or
app-server change. A portable profile snapshot must not replace an externally
managed connection contract.

## Stable Entrypoints

- Codex launcher: `{{CODEX_ENTRYPOINT}}`
- Transport entrypoint: `{{TRANSPORT_ENTRYPOINT}}`
- Proxy or direct wrapper: `{{NETWORK_WRAPPER_OR_NONE}}`
- App-server startup owner: `{{APP_SERVER_STARTUP_OWNER}}`
- Managed runtime category: `{{RUNTIME_CATEGORY}}`
- Repository work-root category: `{{WORK_ROOT_CATEGORY}}`

Entrypoints must describe user-invoked interfaces, not embedded credentials or
an assumed shell mutation.

## Network Routes

| Route | Purpose | Endpoint category | Authentication category | Direct/proxy policy | Owner |
| --- | --- | --- | --- | --- | --- |
| `{{ROUTE_ID}}` | `{{PURPOSE}}` | `{{ENDPOINT_CATEGORY}}` | `{{AUTH_CATEGORY}}` | `{{ROUTE_POLICY}}` | `{{OWNER_ROLE}}` |

- Small direct-access preflight: `{{LOW_TRAFFIC_PREFLIGHT}}`
- Escalation entrypoint after a direct failure: `{{USER_CONTROLLED_FALLBACK}}`
- Revocation or disable path: `{{REVOCATION_WORKFLOW}}`

Store only route categories and reviewed entrypoints here. Keep tokens,
passwords, cookies, keys, authenticated URLs, and secret environment values in
their dedicated credential mechanisms.

## Health Verification

- Low-risk connectivity check: `{{CONNECTIVITY_CHECK}}`
- Launcher or service status check: `{{STATUS_CHECK}}`
- Expected healthy signal: `{{HEALTHY_SIGNAL}}`
- Expected failure classification: `{{FAILURE_CLASSIFICATION}}`
- Maximum bounded check duration: `{{CHECK_DURATION}}`

Verification must be non-destructive and small enough to distinguish transport,
authentication, proxy, launcher, and service failures without exposing secret
values.

## Logs And Diagnosis

- Primary log category or location: `{{PRIMARY_LOG_REFERENCE}}`
- Secondary diagnostic source: `{{SECONDARY_DIAGNOSTIC_REFERENCE}}`
- Redaction boundary: `{{REDACTION_RULE}}`
- Bounded inspection command: `{{BOUNDED_LOG_CHECK}}`
- Dynamic facts to re-check: `{{DYNAMIC_FACTS}}`

Do not copy whole logs into durable profile artifacts. Record only the evidence
needed to locate and classify a failure.

## Recovery And Rollback

- Last-known-good reference: `{{LAST_KNOWN_GOOD_REFERENCE}}`
- Backup location category: `{{BACKUP_LOCATION_CATEGORY}}`
- Rollback owner: `{{ROLLBACK_OWNER_ROLE}}`
- Stop condition: `{{STOP_CONDITION}}`
- Restore sequence: `{{RESTORE_SEQUENCE}}`
- Post-restore verification: `{{POST_RESTORE_CHECK}}`

Rollback must preserve the external control-plane owner's contract and stop for
new authority when recovery would touch credentials, broaden access, or replace
an unowned launcher or service.

## Known Limitations

- Unsupported route or environment: `{{UNSUPPORTED_CASE}}`
- External dependency: `{{EXTERNAL_DEPENDENCY}}`
- User action required: `{{USER_ACTION}}`
- Evidence gap: `{{UNVERIFIED_ASSUMPTION}}`

## Verification Record

- Last verified: `{{DATE_AND_TIME_ZONE}}`
- Runtime or client version category: `{{VERSION_REFERENCE}}`
- Verified by: `{{VERIFIER_ROLE}}`
- Evidence boundary: `{{WHAT_WAS_AND_WAS_NOT_TESTED}}`
- Re-check trigger: `{{CHANGE_OR_EXPIRY_TRIGGER}}`
- Re-check command: `{{LOW_RISK_RECHECK}}`
