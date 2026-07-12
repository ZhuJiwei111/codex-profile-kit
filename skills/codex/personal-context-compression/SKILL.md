---
name: personal-context-compression
description: Use when a long session needs a compact continuation summary with verified state, decisions, risks, and next actions; not for persistence or native compaction.
---

# Personal Context Compression

Create one self-contained continuation snapshot from the current session. It is
context for the next agent, not proof, authorization, durable storage, or Codex
native compaction. Use the user's working language while preserving exact
technical identifiers.

## Scope Gate

Use this skill only to convert accumulated current-session evidence into a
compact continuation summary.

Do not use it to:

- narrow future retrieval or tool output; route that work to
  `personal-context-optimization`;
- save, restore, or write a durable cross-session packet;
- create, update, roll over, archive, or approve planning records;
- obtain fresh process state, progress, or ETA;
- diagnose a failure or declare its root cause;
- produce a reader-oriented project explanation or decision report;
- configure, invoke, or troubleshoot Codex native compaction.

A complex task, a long-running job, or a large context is not enough by itself.
Use compression when accumulated history is impairing reliable continuation or
when an adjacent workflow explicitly requests a bounded candidate summary.

## Summary Contract

Produce one self-contained snapshot. Use only sections that carry material
state:

1. **Goal and constraints**
   - active objective and acceptance condition;
   - user constraints, scope exclusions, and authorization boundaries;
   - external actions that were not performed.
2. **Verified current state**
   - completed, in progress, not started, and blocked work;
   - current `cwd`, worktree, branch, or owner only when evidenced;
   - evidence cutoff and whether verification followed the last relevant change.
3. **Artifacts**
   - exact path, URL, reference ID, symbol, or section;
   - operation: read, modified, created, generated, deleted, or renamed;
   - role: source/config, user or uncommitted work, generated artifact,
     log/checkpoint, temporary/intermediate, planning/context record, or
     sensitive path;
   - purpose, ownership, and current status only when known.
4. **Decisions**
   - active decision and concise rationale;
   - user approval, assumption, or evidence supporting it;
   - superseded or reversed decisions when they explain current state.
5. **Evidence and failures**
   - command, `cwd`, exit status, and relevant output span;
   - minimal exact error text with secrets redacted;
   - tests, metrics, versions, hashes, and other decision-critical evidence.
6. **Unknowns, risks, and blockers**
   - separate facts from hypotheses;
   - mark stale, contradicted, unverified, or invalidated state explicitly.
7. **Next safe actions**
   - first concrete action and any ordered follow-ups;
   - expected verification;
   - approval or new authority required before execution.

## Evidence Discipline

- Process new material incrementally, but emit a self-contained current snapshot,
  not a delta that depends on an older summary.
- Treat a prior summary as evidence input, not authoritative truth. Reconcile it
  against later evidence; do not blindly merge stale tests, paths, decisions,
  status, or next steps.
- When provenance affects continuation, label a fact as `observed`,
  `user-provided`, `inferred`, `unverified`, or `invalidated`.
- Preserve retrievability:
  - files: path plus symbol, stable nearby text, or useful range;
  - commands: command plus `cwd`, exit status, and relevant output;
  - documents: URL or reference ID plus version, date, or section;
  - logs and dynamic state: query or status command plus evidence cutoff.
- Preserve numbers with units, denominator or population when relevant, source,
  and `as_of`. Distinguish measured, configured, planned, and estimated values.
- Preserve unresolved failures with the first failing condition, a minimal exact
  error excerpt, and unresolved hypotheses. Do not turn a hypothesis into a
  root-cause conclusion.
- Treat tool schemas, API shapes, and code as external authorities. Keep a stable
  source anchor and only the minimum exact fragment needed to continue; do not
  paraphrase a contract as if the summary were authoritative.
- Prefer evidence already present. Run only a bounded read-only check when one
  critical field can be resolved cheaply and within scope. Otherwise mark it
  unknown. Do not run a full suite, poll a job, or mutate state merely to improve
  the summary.
- Preserve concise decision rationale, not private chain-of-thought or discarded
  exploratory reasoning.

## Sensitive Data

- Never include a raw token, password, cookie, private key, authenticated URL,
  secret environment value, or credential-bearing command.
- Replace sensitive values with `<REDACTED>`. Preserve only the variable or
  config key, path or category, operational consequence, and required next
  action.
- Do not partially reproduce a secret and do not read a secret-bearing file only
  to make the summary more complete.
- Redact sensitive substrings inside commands, errors, logs, URLs, and examples
  before preserving the surrounding evidence.

## Collaboration Boundaries

- `personal-context-optimization` may supply bounded retrieval results and
  evidence anchors; compression converts them into one continuation snapshot.
- The explicit context save/restore workflow owns durability, packet paths,
  immutable snapshots, and restore-time freshness checks. It may persist a
  compression payload, but compression does not write or restore it.
- `personal-planning-with-files-zh` owns plan selection, lineage, preview,
  approval, rollover, archive, and writes under `.planning/`. Compression may
  produce a candidate seed only from the bounded input planning supplies.
- When explicitly invoked, `personal-long-job-status` owns its one-shot status
  and ETA report. Otherwise fresh status follows the ordinary read-only status
  path; compression never fetches it. If an existing job handoff is included
  here, preserve its identifiers and `as_of` without polling or recomputing it.
- `personal-evidence-debugging` owns reproduction and root-cause investigation.
  Compression carries only the unresolved evidence, hypothesis status, and next
  check.
- `personal-project-output-explainer` owns reader-oriented explanation,
  significance, and decision presentation.

## Acceptance Check

Before returning the snapshot, confirm:

- Can the next agent state the exact goal, constraints, and authorization limit?
- Can it distinguish current work from completed, stale, and unverified state?
- Can it locate every decision-critical file, command, error, and numeric claim?
- Does the latest verification clearly follow, or fail to follow, the latest
  relevant change?
- Is the first next action safe and its required authority explicit?
- Are all sensitive values absent or replaced with `<REDACTED>`?
- Could the snapshot stand alone without rereading the entire prior session?

If evidence is missing, say so. Do not fill gaps with fluent prose.

## Maintenance Reference

Read [source notes](references/source-notes.md) only when auditing or updating
this skill.
