---
name: warn-gpu-task-without-device-scope
enabled: true
event: bash
action: warn
conditions:
  - field: command
    operator: regex_match
    pattern: (?i)(^|[\s;&|()])(?:torchrun|deepspeed|accelerate\s+launch|python3?\s+[^;\n]*\b(?:train|finetune|fine_tune|pretrain|eval|evaluate|inference)[A-Za-z0-9_.-]*\.py)\b
  - field: command
    operator: regex_not_match
    pattern: (?i)(?:CUDA_VISIBLE_DEVICES\s*=|--(?:device|devices|gpu)(?:=|\s))
  - field: command
    operator: regex_not_match
    pattern: (?i)(?:--help|-h|--version)(?:\s|$)
---

This looks like a GPU launch without an explicit device scope. Check current
device availability and select the intended device before launching.
