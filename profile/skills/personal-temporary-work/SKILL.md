---
name: personal-temporary-work
description: Use when one-off migration, conversion, repair, inspection, or artifact work might otherwise add permanent code; separate durable behavior from temporary transition work and manage only exact task-created scratch.
---

# Personal Temporary Work

Keep one-time transition logic out of maintained code.

- Durable behavior serves normal future use and belongs to the normal owner.
- Temporary work handles only bounded existing state or artifacts.
- Hybrid work makes the smallest durable future change and handles historical
  state with a temporary helper or direct command.

Use the project's scratch convention or a task-specific temporary directory.
Use a stable project-local scratch path only when recovery, reattachment, or
handoff needs it. Do not add a permanent helper, dependency, ignore rule,
ledger, or framework merely because reuse is possible.

Treat canonical inputs as immutable by default. Define the actual properties to
preserve and use staging, a sample, or a dry run only when it reduces real
transition risk. Verify durable behavior and one-time transition separately.

Delete only exact scratch created by this task after confirming it is
noncanonical, unshared, unambiguous, and no longer useful for recovery. Retain
it when retry or handoff still benefits, and report the path and purpose.
Pre-existing, shared, ambiguous, or material cleanup needs explicit scope.

Read `references/source-notes.md` only when maintaining provenance.
