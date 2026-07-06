---
name: warn-long-running-direct-launch
enabled: true
event: bash
action: warn
conditions:
  - field: command
    operator: regex_match
    pattern: (?i)(^|[\s;&|()])(torchrun|deepspeed|accelerate\s+launch|python3?\s+[^;\n]*\b(train|finetune|fine_tune|pretrain|eval|evaluate|inference|run_experiment|experiment)[^;\n]*\.py|bash\s+[^;\n]*(train|run|eval|experiment)[^;\n]*\.sh)(\s|$)
  - field: command
    operator: not_contains
    pattern: tmux
  - field: command
    operator: not_contains
    pattern: nohup
---

Command looks like a job that may run longer than 10 minutes.

For long-running jobs, default to a detached launcher instead of keeping the job
attached to a Codex tool session. Prefer `tmux` when reattachment or interaction
matters, and `nohup` for simple one-command runs. Include explicit log/output
paths, expected artifacts, and hand off the session or process id.

After detached launch, the main process may run a read-only startup guard by
default, but it must be capped at 10 minutes and limited to launch validation.
If the startup guard finds immediate failure, missing launch evidence, no first
progress signal after warmup, resource errors, or unexplained GPU abnormalities,
report the anomaly instead of extending the guard. Long-term monitoring requires
current-stage user authorization and an inline monitoring contract.
