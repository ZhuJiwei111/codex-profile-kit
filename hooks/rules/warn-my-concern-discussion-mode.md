---
name: warn-my-concern-discussion-mode
enabled: true
event: prompt
action: warn
pattern: 我的concern
---

Detected `我的concern` in the user prompt.

Treat this as a discussion signal. Unless the user clearly asks for immediate
implementation, do not mutate files or mechanically follow the provisional
idea. First reason about the concern, explain tradeoffs, offer recommendations,
ask targeted questions when needed, and push back on risky or misaligned
directions.
