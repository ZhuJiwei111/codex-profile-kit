---
name: warn-long-running-monitoring
enabled: true
event: bash
action: warn
pattern: (?i)(\bwatch\s+|\btail\s+[^\n;|]*(?:--follow|-[A-Za-z]*f[A-Za-z]*)\b|\bnvidia-smi\b[^\n;|]*(?:-l(?:ms)?\b|--loop(?:-ms)?(?:\b|=))|\bwhile\s+(?:true|:)(?:\s|;|$))
---

This is a continuous monitoring pattern. For a long job, use only a bounded
check unless active monitoring was explicitly authorized for the current stage.
