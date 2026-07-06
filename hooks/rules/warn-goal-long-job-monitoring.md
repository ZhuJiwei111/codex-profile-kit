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

For long jobs, launch detached and define Plan vs Actual. The main process may
run a read-only startup guard by default, but it must be capped at 10 minutes and
limited to launch validation. After that, do not keep waking a worker goal to
poll logs, artifacts, or GPU state.

Only use active monitoring when the user authorized it for the current stage.
Then define an inline monitoring contract with health signals, job-specific
thresholds, fallback thresholds, read-only diagnostics, event triggers,
forbidden actions, record path, report format, stop/timeout condition, and
preapproved next actions. The worker should become a persistent supervisor
waiting for monitoring subAgent events, not a self-waking polling loop.

Fallback anomaly checks should cover process/session problems, stalled progress,
GPU anomalies, resource pressure, error signals, and result or metric anomalies.
Non-target processes sharing a GPU are background context only and must not
trigger an anomaly by themselves.
