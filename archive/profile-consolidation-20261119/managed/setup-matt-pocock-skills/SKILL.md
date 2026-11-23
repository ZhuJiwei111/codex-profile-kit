---
name: setup-matt-pocock-skills
description: Manual only. Configure missing engineering-skill conventions when the user requests repository setup.
---

# Setup Matt Pocock Skills

Inspect the existing instructions, tracker documentation, domain glossary, ADR
owner, and project structure. Reuse them rather than scaffolding parallel files.
Only a selected workflow's actual missing configuration needs setup.

When a tracker choice is genuinely open, explain local Markdown versus the
user's existing issue service and wait for that choice. Do not assume GitHub
from an absent configuration. Read only non-secret repository metadata.

Within the approved setup, document the selected tracker operations and only
labels that the real workflow consumes. Use the existing glossary owner,
including GLOSSARY.md, CONTEXT.md, or a work-line glossary. Prefer GLOSSARY.md
only for a needed new glossary; do not rename project files during setup.

Change AGENTS.md or CLAUDE.md only when requested or necessary within the
approved setup. Do not install plugins, add hooks, mutate tracker state, or
create credentials as an implied setup step. Verify links and the actual
configured local operations, then report what was configured and what still
requires user or service setup.
