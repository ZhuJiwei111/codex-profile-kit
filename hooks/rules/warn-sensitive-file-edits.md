---
name: warn-sensitive-file-edits
enabled: true
event: file
action: warn
conditions:
  - field: file_path
    operator: regex_match
    pattern: (?im)(^|/)(?:\.env(?:\.(?!(?:example|sample|template)$)[^/\n]+)?|\.npmrc|\.pypirc|cookies?\.txt|credentials?(?:\.(?:json|ya?ml|toml|ini))?|secrets?(?:\.(?:json|ya?ml|toml|ini))?|[^/\n]+\.pem)$
---

This edit may touch credential-bearing configuration. Continue only if the
current request explicitly authorizes it, and never expose secret values.
