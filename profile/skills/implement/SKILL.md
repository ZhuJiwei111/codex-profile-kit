---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

Use /tdd where possible, at pre-agreed seams.

Run project-required checks and focused checks for the changed behavior. Run
the full suite when the project requires it or affected integration warrants it;
repeat checks only for new changes, failures, or unresolved concerns.

Once done, use /code-review to review the work.

Commit only with matching Git authority already granted by the user. Otherwise
return the verified implementation without adding a commit approval gate to
the implementation itself.
