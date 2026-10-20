---
name: personal-code-documentation
description: Manual only. Create, audit, or synchronize durable technical documentation for a named code, CLI, API, configuration, or workflow contract.
---

# Personal Code Documentation

Write the smallest durable document that lets its intended reader complete the
requested task. Conversational explanation does not need a documentation file.
For skills, AGENTS instructions, or model-facing workflow rules, use
`writing-for-agents`; this entry owns human-facing technical documentation.

1. Resolve the requested audience, topic, destination, and existing document
   owner. Edit the source of generated documentation, not the generated copy.
2. Inspect the implementation, tests, schemas, and examples relevant to that
   contract. Use a branch diff only for a branch-scoped request; a topic-scoped
   correction is not limited to recently changed files.
3. Patch an identified stale statement in place. For new material, organize
   around the reader's task and reuse existing information architecture.
   Preserve exact commands, identifiers, defaults, version conditions, and
   errors. Distinguish current released behavior from proposed or unshipped
   behavior when that distinction affects the reader.
4. Check the changed text in context and run relevant existing documentation
   or example checks. State which examples were run and which remain illustrative.

Audit-only requests return findings without edits. Source inspection alone
cannot establish deployment state, performance, historical intent, or runtime
success. Mark a material inference or evidence gap rather than filling it in.
Do not expand a factual correction into a tutorial, repository map, or second
documentation owner.

Read `references/source-notes.md` only when maintaining provenance.
