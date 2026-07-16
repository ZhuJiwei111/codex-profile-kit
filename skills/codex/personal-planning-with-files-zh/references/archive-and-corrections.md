# Snapshots, Corrections, Archive, And Successors

Use this reference only for a material correction, terminal archive, or a
successor after closure.

## Non-Sensitive Snapshots

Before correcting an approved fact that does not change the plan contract,
preserve the exact affected controlled files at the following path only after
confirming that neither the files nor their history contain sensitive values:

```text
<project-root>/.planning/snapshots/<YYYYMMDD-HHMMSS>-<slug>/
```

Include `SNAPSHOT.md` with:

- plan ID and operation;
- source paths and SHA-256 hashes;
- evidence cutoff and reason;
- root status and active phase at capture; and
- the approved correction or archive preview that consumes it.

Copy only the affected root/phase files. A snapshot is evidence, not another
active plan, an initialization source, or a mutable trust state. Never add an
active pointer, generation number, packet selector, transaction phase, or trust
enum to it.

Do not make an exact snapshot merely because a correction is material. If the
affected bytes contain or may contain a token, password, cookie, private key,
authenticated URL, credential-bearing environment value, or other sensitive
material, use the sensitive-correction contract below instead.

## Corrections

For a non-sensitive correction that preserves the existing goal, scope, global
acceptance, phase order, closed-phase validity, and lifecycle:

1. Quarantine the affected claim in current reasoning.
2. Show the exact current files, hashes, error, corrected evidence, and impact.
3. Obtain approval for the snapshot and active-file edits.
4. Create the snapshot, update only the canonical active files, and append a
   concise correction note under the snapshot's `corrections/` directory.
5. Validate the resulting serial state and read back the changed claims.

Correction notes identify the original problem, corrected evidence, affected
acceptance or decisions, required revalidation, and approval. They do not alter
the snapshot body. Ordinary fact or evidence correction preserves the root and
phase lifecycle. Never change an `active` or `closed` root or phase back to
`draft`.

While the project is still draft, its proposed goal, scope, acceptance, and
phase order may be revised under a fresh preview. Once active, a change to the
global goal, scope, acceptance, or phase order, or a change that invalidates a
closed phase, is not an in-place correction: record the reason, close the source
when appropriate, and use the successor workflow.

## Sensitive Corrections

Never preserve secret-bearing bytes in `snapshots/` or copy them into an
archive. Remove the value from every authorized in-scope active location, then
create only a redacted incident/correction record containing:

- the sensitive category, never the value;
- affected paths and the bounded removal scope;
- which copies were cleared or remain unverified;
- necessary non-secret evidence and its cutoff; and
- the separate rotation or revocation decision, if any.

Do not record a digest when it could help confirm or recover a low-entropy
secret. A digest is not automatically safe evidence. Credential rotation,
revocation, external cleanup, and repository-history rewriting remain separate
authority.

## Terminal Archive

Terminal archive uses a simple publish-verify-remove-postflight sequence:

1. While the closed active source still exists, run the validator with
   `--operation archive`. This is preflight only: the root must be closed, every
   phase closed, and no active pointer or duplicate truth present.
2. After separate approval, publish one closed copy at:

```text
<project-root>/.planning/archive/<plan-id>/
```

3. Write `ARCHIVE.md` with every copied relative path and source SHA-256, closure
   evidence, skipped checks, and final evidence cutoff. Copy the root, every
   phase trio, and only relevant confirmed non-sensitive snapshots. Refuse an
   existing non-identical destination and never overwrite an archive.
4. Independently compare the manifest to the source set and verify every copied
   hash. The validator checks path safety and lifecycle; it does not prove that
   an archive copy is complete or equal to its source.
5. Only after the manifest and hash comparison passes, remove the active root
   `task_plan.md` and active `.planning/plans/`. Preserve the verified archive
   and other safe history.
6. Run `--operation init` as postflight. It must report `initializable`: the
   active namespace is empty and all surviving historical namespaces are safe.
   An existing safe archive does not block initialization.

If publication or removal is interrupted, preserve both copies until the
manifest, hashes, and ownership are clear. Do not delete an uncertain copy
merely to obtain a clean layout. This sequence is recoverable but is not a
cross-file atomic transaction.

## Successors

A closed plan never reopens. Continued work uses an explicitly approved new
draft with a new `plan_id` and a fresh ordered phase list.

If the closed active source still exists, use `--operation successor` only as a
preflight. Before creating the successor:

- validate the closed source with `--operation successor`;
- name the source archive and the reason for continuation in prose;
- revalidate inherited evidence and dynamic facts;
- show which decisions are inherited, corrected, or deliberately omitted; and
- obtain approval for the exact successor draft.

If the source has already been archived and removed from the active namespace,
do not use `successor`: first validate `ARCHIVE.md` against the archive files and
their hashes, then run `--operation init`, preview the new draft, and initialize
it. After either branch creates the draft, use `--operation inspect` for the
post-mutation validation.

Do not encode predecessor, parent, root-plan, packet, generation, or correction
selectors in active frontmatter. The source archive is historical evidence, not
authority for the successor or its first phase.

## Verification

Before reporting one of these operations complete, verify:

- approval-bound source hashes and exact paths;
- the active root and phase set remain serial and single-writer;
- snapshots or archive controls identify every copied file;
- sensitive corrections contain only redacted categories, paths, removal scope,
  and necessary non-secret evidence;
- corrections remain discoverable without rewriting snapshots;
- an archive is closed, its destination is unique, and its manifest and copied
  hashes were compared independently of the validator;
- archive postflight reports an initializable empty active namespace;
- a successor is a separately approved draft with no active phase; and
- no implementation, Git, publication, or later phase action was inferred.
