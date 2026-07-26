---
name: personal-code-documentation
description: Manual only. Use only when the user explicitly invokes this skill to create, substantially rewrite, audit, or synchronize durable technical documentation derived from a codebase or an identified CLI, API, configuration, installation, or workflow contract.
---

# Personal Code Documentation

Create the smallest durable document that lets its intended reader complete the
requested task. Do not use this skill for conversational explanation, status,
diagnosis, review, or expression-only polishing.

## Establish The Contract

- Follow the requested audience, format, and path. Otherwise infer the narrowest
  actual reader and canonical documentation owner.
- Check whether the target is generated; edit its source or generator.
- Identify the reader's goal, included boundary, and material non-goals. Ask
  only when an unresolved public-contract or ownership choice changes the
  result.

## Build Bounded Evidence

Inspect only the source, tests, schemas, and existing docs needed to establish
the relevant entry points and contracts. Preserve exact identifiers, commands,
paths, configuration keys, and error text.

Do not infer deployed state, performance, security, reliability, or historical
rationale from source alone. Label a material inference or omission; do not
turn a documentation request into a broad diagnosis.

## Write And Check

- For an identified stale contract, patch the smallest factual surface.
- For a new document, organize around the reader's task rather than repository
  traversal. Include only sections needed for that outcome.
- For a requested tutorial, state prerequisites, steps, observable checks, and
  the expected result. Mark illustrative commands that were not run.
- Avoid duplicate owners, exhaustive matrices, repeated background, fixed
  templates, and tutorial expansion when a concise reference is enough.

Read the edited text in context, inspect the scoped diff, and run the narrow
existing documentation or example checks that matter. Report what was and was
not verified.

Read `references/source-notes.md` only when maintaining provenance.
