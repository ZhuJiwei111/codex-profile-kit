---
name: to-spec
description: Manual only. Turn an agreed discussion into a concise implementation specification, using the requested local or published destination.
---

# To Spec

Synthesize what is already agreed. Inspect the affected code and existing
requirements only where they can change the specification. Ask about an actual
blocking decision, not a mandatory interview or test-seam confirmation.

Use the existing specification owner and format. Include the problem, intended
behavior, material decisions, acceptance checks, scope limits, and unresolved
questions that actually matter. Scale detail to the change; do not invent a
long user-story list or fill empty template sections. Keep precise interfaces,
examples, or source paths when they clarify the contract.

Reuse existing test boundaries and describe observable acceptance behavior.
Keep assumptions distinguishable from user decisions. Do not implement while
producing the specification.

Save to the requested local owner. Publish an issue, apply labels, or update an
external tracker only when that destination and write are authorized; otherwise
return the draft. Missing tracker setup does not block a local specification.
