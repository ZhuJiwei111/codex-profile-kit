---
name: warn-gpu-task-without-device-scope
enabled: true
event: bash
action: warn
conditions:
  - field: command
    operator: regex_match
    pattern: (?i)(^|[\s;&|()])(torchrun|deepspeed|accelerate\s+launch|python3?\s+[^;\n]*\b(train|finetune|fine_tune|pretrain|eval|evaluate|inference)[^;\n]*\.py)(\s|$)
  - field: command
    operator: not_contains
    pattern: CUDA_VISIBLE_DEVICES
---

GPU-looking task without `CUDA_VISIBLE_DEVICES` detected.

Before heavy GPU work, check `nvidia-smi`, choose an explicit device scope, and
ask before launching long-running or heavy jobs.
