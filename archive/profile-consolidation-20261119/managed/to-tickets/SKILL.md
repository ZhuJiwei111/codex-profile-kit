---
name: to-tickets
description: Manual only. Split an agreed specification into independently verifiable work items with explicit dependencies.
---

# To Tickets

Read the named specification and the relevant affected flow. Preserve the
agreed scope; surface a missing prerequisite instead of silently enlarging it.

Choose the fewest useful vertical slices. Each ticket should have a concrete
outcome and acceptance check, its relevant interfaces or existing source owner,
and any actual blocking tickets. A slice spans only the layers the behavior
needs, not every layer in the application. Add prefactoring only for observed
coupling that blocks the requested change.

Keep decisions and dependencies explicit enough that a new worker can act
without reconstructing the whole chat. Do not prescribe a fresh session per
ticket or introduce a second plan alongside an active canonical plan.

Use the requested destination and existing ticket conventions. Draft locally
or in chat when external publication is not authorized. Creating issues,
comments, labels, branches, or worktrees requires the matching authority; a
ticket-writing request alone is not implementation authority.
