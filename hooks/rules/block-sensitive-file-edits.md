---
name: block-sensitive-file-edits
enabled: true
event: file
action: block
conditions:
  - field: file_path
    operator: regex_match
    pattern: (?im)(^|/)(?:\.netrc|id_(?:rsa|dsa|ecdsa|ed25519)(?:\.[^/\n]+)?|[^/\n]*private[^/\n]*\.pem|[^/\n]+\.(?:key|p12|pfx)|\.secrets(?:/.*)?|\.codex/(?:auth(?:\.json)?|credentials|tokens?|sessions?|archived_sessions|history\.jsonl|session_index\.jsonl)(?:/.*)?)$
---

Editing credential stores, Codex auth/session data, `.netrc`, or private-key
material is blocked. Use a dedicated user-controlled credential workflow.
