---
name: domain-modeling
description: Clarify domain terminology and relationships, or create or revise a glossary or architectural decision when that work is requested.
---

# Domain Modeling

Resolve overloaded terms, inconsistent relationships, and consequential domain
choices using concrete scenarios and the code or evidence that actually owns
the behavior. Distinguish current facts, proposed terms, and user decisions.

Use the repository's existing glossary and ADR owners, including work-line
files such as `.agent/GLOSSARY.md` or an established CONTEXT.md. Do not migrate
or duplicate them to follow a preferred filename. If a new owner is needed
within authorized documentation work, prefer GLOSSARY.md and create only the
material that has actually been settled.

For discussion-only requests, propose terms and surface contradictions without
writing new project documents. During authorized documentation work, update the
resolved definition in its canonical owner. Keep glossary definitions separate
from implementation details and task status. Use [CONTEXT-FORMAT.md](CONTEXT-FORMAT.md)
only as a new-glossary example, preserving existing project formats.

Record an ADR only for a real, consequential trade-off whose rationale would
otherwise be lost. Use [ADR-FORMAT.md](ADR-FORMAT.md) when helpful. The skill is
not a requirement to create an ADR for every design decision.
