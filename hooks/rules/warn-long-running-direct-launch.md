---
name: warn-long-running-direct-launch
enabled: true
event: bash
action: warn
conditions:
  - field: command
    operator: regex_match
    pattern: (?i)(^|[\s;&|()])(?:torchrun|deepspeed|accelerate\s+launch|python3?\s+[^;\n]*\b(?:train|finetune|fine_tune|pretrain|eval|evaluate|inference|run_experiment|experiment)[A-Za-z0-9_.-]*\.py|bash\s+[^;\n]*(?:train|run|eval|experiment)[^;\n]*\.sh)\b
  - field: command
    operator: regex_not_match
    pattern: (?i)(^|[\s;&|()])(?:tmux|nohup|screen|systemd-run|setsid)(?:\s|$)
  - field: command
    operator: regex_not_match
    pattern: (?i)(?:--help|-h|--version|--dry-run)(?:\s|$)
---

This command may be a long job launched in the foreground. If it is expected to
exceed 10 minutes, use detached execution and only a bounded startup guard.
