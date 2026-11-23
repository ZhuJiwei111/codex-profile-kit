---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Use the user's named destination or an existing project handoff owner. Choose a stable task-owned location when another session must resume from it; avoid duplicating an active plan. Do not force a new chat for related work that can continue here.

Include a skill reference only when the continuation needs a non-obvious workflow.
This entry transfers unfinished work. It does not close or archive the current
chat. An explicit archive request uses the product's native task archive action.
Resolve disputed historical decisions from the named source turns and existing
canonical document within the user's requested scope.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
