---
name: warn-package-manager-install
enabled: true
event: bash
action: warn
pattern: (?i)(^|[\s;&|()])(?:conda\s+(?:env\s+create|install|create)|mamba\s+(?:install|create)|python3?\s+-m\s+pip\s+install|pip3?\s+install|uv\s+(?:sync|add|pip\s+install)|poetry\s+(?:install|add)|npm\s+(?:install|ci)|pnpm\s+(?:install|add)|yarn\s+(?:install|add)|bun\s+(?:install|add)|cargo\s+install|apt(?:-get)?\s+install|dnf\s+install|brew\s+install)(?:\s|$)
---

This command installs dependencies. Confirm that the target environment is
explicit and the operation is authorized. The host-documented Codex fallback's
bounded standing authorization counts; it does not transfer to Conda `base`, a
project environment, or system scope.
