---
name: warn-sensitive-path-command
enabled: true
event: bash
action: warn
pattern: (?i)(^|[\s"'=:/])(\.env(\.[A-Za-z0-9_-]+)?|\.netrc|\.npmrc|\.pypirc|id_(rsa|dsa|ecdsa|ed25519)|[^ \n;&|]*\.(pem|key|p12|pfx)|cookies?\.txt|credentials?(\.(json|ya?ml|toml|ini))?|secrets?[/._-]|\.secrets/env|\.codex/(auth|auth\.json|credentials|tokens?|session|sessions)([/.\s"';&|]|$))
---

Command references a path or filename commonly used for secrets.

Do not print, copy, log, or commit secret values. If inspection is necessary,
report only the path, permission/config category, or redacted placeholders such
as `<REDACTED>`.
