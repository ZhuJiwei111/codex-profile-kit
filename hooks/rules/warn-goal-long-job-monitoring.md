---
name: warn-goal-long-job-monitoring
enabled: true
event: prompt
action: warn
conditions:
  - field: user_prompt
    operator: regex_match
    pattern: (?is)(\bgoal\b|目标模式|持续推进|持续执行)
  - field: user_prompt
    operator: regex_match
    pattern: (?is)(长任务|long[- ]?running|gpu|训练|training|download|下载|eval|评估|monitor|监控|轮询)
---

Prompt mentions both goal-style continuation and long-job monitoring.

Keep goal mode for bounded stage progress: implementation, short verification,
handoff, and a stage decision. Do not use goal continuation as the monitoring
cadence for long GPU jobs, downloads, evals, or batch work.

For long jobs, launch detached, define Plan vs Actual, and use an authorized
read-only monitoring subAgent. The worker should become a persistent supervisor
waiting for monitor events, not a self-waking polling loop.
