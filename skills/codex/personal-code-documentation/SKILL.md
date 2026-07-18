---
name: personal-code-documentation
description: Use to create new or substantially rewritten codebase-derived technical documentation, including tutorials, or to synchronize existing documentation made stale by an identified CLI, API, configuration, installation, or workflow contract change. Not for conversational code explanation, output decoding, status, diagnosis, review, or prose-only polishing.
---

# Personal Code Documentation

Create durable technical documentation from bounded repository evidence. Keep
the document accurate for its reader without taking ownership of code changes,
live project state, diagnosis, or publication.

## Choose The Mode

- document: create or substantially rewrite an architecture guide, API or
  reference page, onboarding guide, walkthrough, or other lasting artifact.
  Treat tutorial as a document subtype with an executable learning outcome.
- sync_existing: patch an existing supported page after an identified stable
  contract change makes it stale.

Do not use this skill for a conversational explanation of code. Use
personal-project-output-explainer for an explicitly requested explanation of an
existing task output, and personal-writing-polish for expression-only editing.

## Establish The Reader And Owner

Follow an explicit audience, format, and path. Otherwise infer the narrowest
reader who must use the artifact, such as an API caller, maintainer,
contributor, or operator.

Before editing:

- identify the canonical source, existing documentation convention, and target
  path;
- check whether the target is generated and edit its source or generator
  instead of the generated output;
- define the reader's goal, the included boundary, and material non-goals; and
- ask only when an unresolved audience, owner, or public-contract choice would
  materially change the document.

## Build Bounded Evidence

Inspect the smallest source set that establishes the relevant entry points,
behavior, interfaces, state, dependencies, examples, and verification surface.
Expand along actual control, data, or API boundaries rather than scanning the
whole repository by default.

Keep these limits:

- Source establishes current structure and static behavior, not deployed state,
  performance, security, reliability, or historical rationale by itself.
- State rationale or history only when comments, ADRs, issues, or commit
  evidence support it; otherwise label the interpretation or omit it.
- Preserve exact paths, identifiers, commands, APIs, configuration keys, and
  error text.
- Treat contradictions between code, schemas, tests, and docs as evidence gaps;
  do not turn the documentation task into diagnosis.

## Write A Document

Organize around the reader's task and decisions, not repository traversal order.
Include only sections the artifact needs. Prefer stable symbols, paths, API
names, and schema fields over fragile line anchors.

For a tutorial:

- state the outcome, prerequisites, initial state, and expected final result;
- order steps by dependency and give each meaningful step an observable check;
- distinguish commands and examples that were run from illustrative ones; and
- include recovery or cleanup only where a plausible failure needs it.

Verify runnable examples when practical. If an example was not run, say so
instead of presenting it as demonstrated.

## Synchronize Existing Documentation

Use sync_existing only when the stale contract is already identified.

1. Confirm the before-and-after contract and the canonical owning page.
2. Search only the likely owning docs and the changed public symbols or settings.
3. Patch the smallest factual surface needed for accuracy.
4. Preserve generated, historical, versioned, translated, or frozen material
   according to its owner.
5. Route a new document, tutorial, or information-architecture redesign back to
   document mode.

## Verify And Report

Read the edited section in context and inspect the scoped diff. Check affected
links, commands, snippets, terminology, and stale semantic anchors with the
repository's narrow existing checks. Report what was verified, what was not run,
and any evidence gap. After file changes, final completion remains with
personal-risk-verification.

Read references/source-notes.md only when maintaining provenance or revising
this skill.
