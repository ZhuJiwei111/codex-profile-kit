---
name: research
description: Investigate a question against primary sources and return cited findings. Use when the user requests research, documentation or API fact gathering, or delegated reading; save a report only within the requested output scope.
---

Investigate in the main task by default. Delegate only when the user or applicable
repository instructions authorize it and independent reading materially helps;
then follow `personal-subagent-boundaries` and retain the final judgment here.

Workflow:

1. Investigate the question against **primary sources** — official docs, source code, specs, first-party APIs — not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Return the supported findings and material uncertainty with source citations.
3. Save a Markdown report only when the user requests a file or existing task
   authority includes that output. Use the named destination or established
   repository convention. Research alone does not authorize repository changes,
   external messages, publication, or Git actions.
