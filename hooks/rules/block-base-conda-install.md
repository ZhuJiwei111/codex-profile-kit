---
name: block-base-conda-install
enabled: true
event: bash
action: block
pattern: (?i)(^|[\s;&|()])(?:(?:conda|mamba)\s+(?:env\s+create|install|create)\b[^\n;&|]*(?:(?:-n|--name)(?:\s+|=)base\b|(?:-p|--prefix)(?:\s+|=)[^ \n;&|]*/(?:(?:mini)?conda[0-9A-Za-z_.-]*|anaconda3)\b(?=$|["'\s;&|)]))|conda\s+run\b[^\n;&|]*(?:-n|--name)(?:\s+|=)base\b[^\n;&|]*(?:pip3?|python3?\s+-m\s+pip|conda|mamba)\s+install\b|conda\s+activate\s+base\b[^\n;&|]*(?:&&|;)\s*(?:pip3?|python3?\s+-m\s+pip|conda|mamba)\s+install\b)
---

An install explicitly targets the Conda `base` environment. Keep `base`
minimal. Use the project's explicit environment or the host-documented Codex
fallback when its bounded authorization applies.
