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

For long-running GPU jobs, include the expected device scope in the Plan vs
Actual mapping and startup guard. During the bounded startup guard, verify that
the target process uses the expected device(s) and watch for obvious low
utilization, unexplained 0-100 utilization thrashing, missing device use, memory
errors, or CUDA errors. Non-target processes sharing the same GPU are background
context only and should not trigger an anomaly by themselves.
