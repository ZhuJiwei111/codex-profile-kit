---
name: block-base-conda-install
enabled: true
event: bash
action: block
pattern: (?i)(^|[\s;&|()])((conda|mamba)\s+install\b[^\n;&|]*\s(-n|--name)\s+base\b|(conda|mamba)\s+install\b[^\n;&|]*\s(-p|--prefix)\s+[^ \n;&|]*/(mini)?conda[0-9A-Za-z_.-]*\b|(conda|mamba)\s+install\b[^\n;&|]*\s(-p|--prefix)\s+[^ \n;&|]*/anaconda3\b|conda\s+activate\s+base\b[^\n;&|]*(pip|conda|mamba)\s+install\b)
---

Install into the `base` conda environment is blocked.

Keep `base` minimal. Use or create a project-specific environment, preferably
under the host's project environment directory, and ask the user if the intended environment
is unclear.
