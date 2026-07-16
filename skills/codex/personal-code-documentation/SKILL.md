---
name: personal-code-documentation
description: Use to explain existing code, create new or substantially rewritten technical documentation, or run sync_existing for existing docs made stale by an identified CLI, API, config, installation, or workflow contract change; not for output decoding, diagnosis, review, status reporting, or prose-only polishing.
---

# Personal Code Documentation

Turn verified repository evidence into a code explanation, a durable technical
document, a runnable learning path, or the smallest factual synchronization of
existing stale documentation. Own the audience, information structure, source
anchors, and evidence boundary of that output. Do not absorb code
implementation, defect review, failure diagnosis, status reporting, or
expression-only rewriting.

## Keep The Actor Boundary

The main process locks mode, audience, scope, authority, and evidence needs,
then performs intake and owns any task-level verdict. A bounded documentation
executor performs substantive repository reading, file edits, and validation.
An independent reviewer may report semantic evidence, coverage gaps, and
uncertainty, but never decides acceptance or completion. Simple work may use
one executor across several evidence layers; do not manufacture delegation
when it adds no independence or useful coverage.

## Apply The Source-Object Gate

Use this skill only when the primary source object is existing code or a
codebase-derived artifact that the user wants created. Before selecting a mode:

- route an existing Codex response, project result, evidence chain, artifact
  summary, or decision rationale to `personal-project-output-explainer`;
- keep a bounded patch to existing docs made stale by an already identified
  contract change in this skill and select `sync_existing`;
- route expression-only revision to `personal-writing-polish`;
- route defect or feedback assessment to `personal-review-response`, failure
  investigation to `personal-evidence-debugging`, and code implementation to
  its implementation workflow; and
- for a mixed request, partition the outputs and use this skill only for the
  code explanation or new/substantially rewritten codebase-derived artifact.

Stop at the routing boundary rather than answering the adjacent request under
this skill. Do not treat the presence of code terms, paths, or documentation as
sufficient reason to stay.

## Select One Primary Mode

| Reader need | Mode | Default artifact |
| --- | --- | --- |
| Understand existing code structure, behavior, flow, or an algorithm | `explain` | Current conversation |
| Create a new or substantially rewrite a lasting architecture, API, reference, onboarding, or walkthrough document | `document` | Explicit or repository-owned documentation path |
| Learn to complete a concrete task through verified steps | `tutorial` | Tutorial or onboarding artifact |
| Update an existing supported page made stale by an identified CLI, API, config, installation, or workflow contract change | `sync_existing` | Small factual patch to the current canonical page |

- Keep `explain` read-only and conversational by default. Write a file only
  when the user explicitly requests a durable artifact; then use `document`.
- Keep `sync_existing` bounded to existing documentation. A new architecture
  guide, explanation, tutorial, migration system, or broad information-
  architecture redesign belongs to `document`, `tutorial`, or the relevant
  design owner. Ordinary status and prose polish are not documentation sync.
- Split a mixed request into explicit outputs rather than forcing one mode over
  every part.
- Handle a simple, explicit explanation or small document directly. Use
  `personal-brainstorms` only when information architecture, scope, audience,
  or a product contract remains consequentially unresolved.

## Lock The Reader And Artifact

Follow an explicitly requested audience, depth, format, and path. Otherwise:

- for `explain`, assume a technically literate reader who does not know this
  local code;
- for `document`, infer the narrowest clear reader from the artifact, such as
  API caller, subsystem maintainer, contributor, or operator; and
- for `tutorial`, state the prerequisites needed to reach the learning outcome.

Ask one targeted question only when a distinction such as public versus
internal, caller versus maintainer, or developer versus operator would
materially change the artifact. Do not ask when repository conventions or the
request already make the choice clear.

For a substantial persistent artifact, keep this compact contract internally:

```yaml
mode:
audience:
reader_goal:
artifact_path:
scope:
source_of_truth:
evidence_revision:
maintenance_owner:
unverified_claims: []
```

Inspect applicable `AGENTS.md`, nearby documentation style, generated-file
ownership, and the canonical source before writing. Do not hand-edit generated
documentation or invent a new documentation root when ownership is clear. If
the repository, instructions, edit surface, generated owner, or verification
command remains unclear after bounded inspection, stop and ask the smallest
question that changes the work.

## Build A Bounded Evidence Map

Inspect the smallest source set that establishes the target boundary, entry
points, relevant dependencies, behavior, and verification surface. Expand
along actual control, data, state, or API boundaries instead of scanning the
whole repository by default.

Keep these evidence classes distinct:

- `observed_source`: current code, configuration, tests, schemas, or canonical
  repository documentation;
- `verified_execution`: a command, test, example, or runtime observation that
  was actually executed;
- `authoritative_external`: current authoritative external documentation that
  was explicitly checked; and
- `inference`: an interpretation not directly established by the sources.

Apply the following claim rules:

- Source inspection can establish structure and static behavior, but not by
  itself production state, deployed configuration, performance, security, or
  operational reliability.
- State design rationale or evolutionary history only when an ADR, comment,
  issue, commit history, or explicit source supports it. Otherwise say that the
  rationale is not recorded or label the explanation as an inference.
- Verify runnable examples when practical. Label an example or command that
  was not run instead of presenting it as demonstrated.
- Treat source-versus-doc, schema-versus-implementation, or example-versus-
  runtime contradictions as evidence gaps. Do not silently choose the more
  convenient version or turn the documentation task into diagnosis.
- Preserve exact identifiers, paths, API names, configuration keys, states,
  and error strings. Explain them without renaming the underlying contract.

Expose uncertainty where it changes how the reader should use the artifact;
do not mechanically label every sentence with an evidence class.

## Explain Existing Code

Lead with the code's purpose and the shortest useful mental model. Then cover
only the dimensions the reader needs:

1. boundary and entry point;
2. inputs, outputs, state, side effects, and external dependencies;
3. control flow, data flow, call path, or algorithm steps;
4. invariants, important branches, failure paths, and cleanup; and
5. verified rationale, material tradeoffs, unknowns, and the best next source
   anchor.

Use concise snippets only when they reduce cognitive load. For conversational
explanations, link precise files and line numbers when available. Do not create
a document, modify code, hunt for unrelated defects, or claim a review verdict
merely because a suspicious pattern appears while explaining it.

## Create Durable Documentation

Read [documentation contracts](references/documentation-contracts.md) for an
architecture guide, API/reference artifact, substantial walkthrough, or any
document whose section selection or validation is non-trivial.

- Organize from the reader's task and decisions, not from repository directory
  order or the order in which files were inspected.
- Include only relevant sections supported by evidence; do not force a
  universal comprehensive template.
- Prefer stable paths, symbols, API names, schema fields, and configuration keys
  over line numbers that will quickly rot. Use exact line anchors primarily in
  the accompanying conversation or when the repository has a refresh process.
- Point to generated specifications and their source or generator rather than
  duplicating large generated inventories by hand.
- Write the prose directly. Use scripts only for reproducible extraction,
  counts, tables, or other mechanical evidence, and route their lifecycle to
  `personal-temporary-work` when they are one-off helpers.
- Do not add documentation generators, CI jobs, hosted sites, publication, or
  deployment merely because the artifact could use them.

## Build A Tutorial

Read [documentation contracts](references/documentation-contracts.md) before
creating a multi-step tutorial or onboarding path.

- Define what the reader will be able to do, the required prior knowledge and
  environment, the initial state, and the expected final result.
- Order concepts and actions by dependency. Keep each step small enough to
  check before building on it.
- Pair commands or actions with expected evidence and frequent checkpoints.
- Include common errors only when they are plausible and evidence-backed;
  provide recovery, reset, or cleanup where it matters.
- Distinguish executed examples from illustrative ones. Do not introduce an
  intentional failure or mutate project state solely for teaching unless that
  exact exercise is authorized and safely bounded.
- End with a concise recap and a useful next learning or operating action.

## Synchronize Existing Documentation

Use `sync_existing` only after a stable, evidenced CLI, API, config,
installation, or workflow contract change makes an existing supported document
stale. Read [the sync-existing contract](references/sync-existing.md) when more
than one obvious literal, link, example, or snippet may be affected.

- Lock the before/after contract, target version and audience, canonical page,
  generated owner, and narrow validation surface. Stop on an unresolved
  code-versus-specification conflict instead of guessing which side is right.
- Start from the identified change. Run a bounded doc-first search over likely
  owning pages and a bounded code-first mapping from the changed public
  surface. Classify coverage as current, stale, missing a small fact, or
  outside `sync_existing`.
- Patch the smallest factual surface: a literal, link, example, snippet,
  prerequisite, default, or short paragraph needed to make the existing page
  accurate. Preserve historical, versioned, translated, frozen, and generated
  material according to its actual ownership.
- Route a new or substantially rewritten architecture, API, explanation,
  onboarding, tutorial, or navigation structure to the corresponding mode or
  design owner. Do not turn synchronization into a status report or polish
  pass.
- After editing, read the section in context, inspect the scoped diff, search
  for stale semantic anchors, validate affected links/examples/snippets with
  existing narrow checks, and run `git diff --check` in a Git repository.

## Use Visuals Only When They Carry Structure

Choose the smallest form that makes a material relationship easier to verify:

- a table for several exact mappings or comparisons;
- a flowchart for multi-component control or data flow;
- a sequence diagram for interactions among several participants; or
- a state diagram for lifecycle and transition rules.

Keep simple single-path behavior in prose or compact notation. Derive every
node and edge from evidence, preserve real identifiers, and explain the
decision-relevant meaning in text. Do not add decorative diagrams or render an
inference as confirmed architecture.

## Verify The Output And Hand Off

- Re-read an explanation against its source anchors and remove unsupported
  claims or accidental review findings.
- For a persistent artifact, verify its path, audience, links, examples,
  commands, terminology, evidence revision, and unverified items after the last
  documentation edit.
- Use proportionate parser, link, example, or command checks. A successful
  Markdown render does not prove technical accuracy, and runtime tests alone do
  not prove that the document is current.
- After task-owned file changes, hand final completion to
  `personal-risk-verification`. Use `personal-branch-finish` only for a later
  explicit Git-readiness or handoff decision.

## Collaborate Without Blurring Ownership

- This skill owns both `sync_existing` factual synchronization and new or
  substantially rewritten codebase-derived documentation. Keep those modes
  separate so a small stale-contract patch does not become a redesign.
- `personal-project-output-explainer` decodes an existing Codex response,
  project result, evidence chain, or decision rationale. This skill explains
  the codebase itself and creates codebase-derived artifacts. A decoded output
  is context, not automatically repository evidence.
- `personal-writing-polish` changes expression only after this skill has locked
  the facts, structure, terminology, and evidence boundary.
- `personal-review-response` first decides whether review feedback is accepted
  and whether local implementation is authorized. Accepted documentation work
  may then enter this skill.
- `personal-evidence-debugging` owns unexpected failures and contradictions
  that require reproduction or causal investigation.
- `personal-test-first-changes` owns any separately authorized product-code
  behavior change needed by an example or tutorial; documentation authority
  does not authorize that code change.
- `personal-subagent-boundaries` may isolate large independent evidence areas,
  while this skill retains the audience, artifact, synthesis, and evidence
  boundary.

These skills may compose in one request, but each artifact and decision keeps
one owner. Do not let polishing change facts, explanation become diagnosis, or
documentation creation imply code, Git, publication, or external-state
authority.

## Sources

Read [source notes](references/source-notes.md) only when provenance, upstream
comparison, licensing, rename recovery, or local deviations matter.
