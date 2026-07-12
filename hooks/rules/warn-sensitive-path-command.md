---
name: warn-sensitive-path-command
enabled: true
event: bash
action: warn
pattern: (?i)(^|[\s"'=:/])(?:\.env(?:\.(?!(?:example|sample|template)\b)[A-Za-z0-9_-]+)?|\.netrc|\.npmrc|\.pypirc|id_(?:rsa|dsa|ecdsa|ed25519)|[^ \n;&|]*private[^ \n;&|]*\.pem|[^ \n;&|]+\.(?:key|p12|pfx)|cookies?\.txt|credentials?(?:\.(?:json|ya?ml|toml|ini))?|secrets?(?:[/._-]|\b)|\.codex/(?:auth(?:\.json)?|credentials|tokens?|sessions?|archived_sessions|history\.jsonl|session_index\.jsonl))(?:[/\.\s"';&|]|$)
---

The command references a potentially secret-bearing path. Limit inspection to
metadata when possible and report only paths, permissions, or redacted values.
