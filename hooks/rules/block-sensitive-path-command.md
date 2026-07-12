---
name: block-sensitive-path-command
enabled: true
event: bash
action: block
pattern: (?is)(?:\b(?:rm|mv|cp|install|touch|truncate|tee|chmod|chown|ln|unlink|shred|dd)\b[^\n;&|]*(?:\.netrc|id_(?:rsa|dsa|ecdsa|ed25519)|[^ \n;&|]*private[^ \n;&|]*\.pem|[^ \n;&|]+\.(?:key|p12|pfx)|\.secrets(?:/|\b)|\.codex/(?:auth(?:\.json)?|credentials|tokens?|sessions?|archived_sessions|history\.jsonl|session_index\.jsonl))|\b(?:sed|perl)\b[^\n;&|]*(?:-i|-pi)[^\n;&|]*(?:\.netrc|id_(?:rsa|dsa|ecdsa|ed25519)|[^ \n;&|]*private[^ \n;&|]*\.pem|[^ \n;&|]+\.(?:key|p12|pfx)|\.secrets(?:/|\b)|\.codex/(?:auth(?:\.json)?|credentials|tokens?|sessions?|archived_sessions|history\.jsonl|session_index\.jsonl))|(?:^|[;&|])[^;\n&|]*(?:>>?|2>)\s*[^ \n;&|]*(?:\.netrc|id_(?:rsa|dsa|ecdsa|ed25519)|private[^ \n;&|]*\.pem|\.(?:key|p12|pfx)|\.secrets(?:/|\b)|\.codex/(?:auth(?:\.json)?|credentials|tokens?|sessions?|archived_sessions|history\.jsonl|session_index\.jsonl)))
---

A shell mutation targets credential, session, or private-key material. Use a
dedicated user-controlled workflow instead of modifying it through Codex.
