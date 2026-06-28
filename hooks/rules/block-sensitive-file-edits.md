---
name: block-sensitive-file-edits
enabled: true
event: file
action: block
conditions:
  - field: file_path
    operator: regex_match
    pattern: (?i)(^|/)(\.env(\.[^/]*)?|\.netrc|\.npmrc|\.pypirc|id_(rsa|dsa|ecdsa|ed25519)|.*\.(pem|key|p12|pfx)|cookies?\.txt|credentials?(\.(json|ya?ml|toml|ini))?|secrets?[/._-]|\.secrets/env|\.codex/(auth|auth\.json|credentials|tokens?|session|sessions)(/|$))
---

Sensitive file edit detected.

Do not write credentials, tokens, private keys, cookies, authenticated proxy
URLs, or Codex auth/session files. Ask the user for explicit approval and use a
narrow, redacted workflow before touching this file.
