---
name: warn-package-manager-install
enabled: true
event: bash
action: warn
pattern: (?i)(^|[\s;&|()])(conda\s+env\s+create|mamba\s+(install|create)|conda\s+(install|create)|pip\s+install\s+-r|uv\s+sync|npm\s+install|pnpm\s+install)(\s|$)
---

Package-manager operation detected.

Before running dependency installs that may fetch large trees, identify the
intended project environment and ask the user unless this exact operation has
already been approved in the current task.
