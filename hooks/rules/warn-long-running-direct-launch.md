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
paths and hand off the session or process id.
