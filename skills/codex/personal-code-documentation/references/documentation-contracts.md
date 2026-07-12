# Documentation Contracts

Use this reference for substantial `document` and `tutorial` work or a complex
`explain` request. Select only the relevant artifact checklist; do not emit the
whole reference as a template.

## Contents

- [Audience And Artifact Contract](#audience-and-artifact-contract)
- [Evidence And Claim Strength](#evidence-and-claim-strength)
- [Architecture Guide](#architecture-guide)
- [API Or Reference Documentation](#api-or-reference-documentation)
- [Walkthrough Or Code Explanation](#walkthrough-or-code-explanation)
- [Tutorial Or Onboarding](#tutorial-or-onboarding)
- [Visual Selection](#visual-selection)
- [Final Artifact Check](#final-artifact-check)

## Audience And Artifact Contract

Choose an audience from the task the document enables, not a generic expertise
label.

| Artifact | Primary reader | Reader should be able to |
| --- | --- | --- |
| Architecture guide | New subsystem maintainer or reviewer | Locate boundaries, follow interactions, and evaluate a change |
| Internal API reference | Project caller or implementer | Invoke the contract and handle its states and errors |
| Public API guide | External caller | Integrate without relying on repository internals |
| Operations guide | Operator | Configure, observe, recover, and identify escalation signals |
| Onboarding guide | New contributor | Reach a verified working state and make a first bounded change |
| Feature walkthrough | Developer unfamiliar with the path | Trace one behavior from entry to outcome |

Resolve only distinctions that change content. Public versus internal changes
which implementation details and compatibility promises are appropriate.
Caller versus maintainer changes whether internals or usage contracts dominate.
Developer versus operator changes the commands, failure signals, and recovery
surface.

For a durable artifact, establish:

- the canonical path and nearby documentation conventions;
- whether it is handwritten, generated, or partially generated;
- the source revision or evidence time that makes freshness meaningful;
- the source of truth for commands, schema, API, configuration, and examples;
- who or what is expected to update it; and
- which deliberately omitted topics belong elsewhere.

## Evidence And Claim Strength

Use the strongest available evidence without upgrading its meaning.

| Claim | Direct evidence | If unavailable |
| --- | --- | --- |
| A symbol exists and calls another symbol | Current source and exact path | Mark as not inspected |
| A branch produces an error or side effect | Source plus focused test or execution when behavior matters | Describe static behavior only |
| A CLI command works | Current `--help`, parser, test, dry run, or bounded execution | Mark command as unverified |
| An API request or response has a shape | Current schema, implementation, tests, or generated spec | State the observed subset |
| A service is deployed with a setting | Current deployment evidence from the relevant environment | Describe repository configuration, not deployed state |
| A path meets a latency, scale, or security property | Relevant benchmark, runtime evidence, audit, or authoritative contract | Do not make the guarantee |
| A design choice was made for a reason | ADR, issue, comment, commit, or explicit owner statement | Label a plausible explanation as inference |
| A workflow is supported externally | Current authoritative external documentation | State that external support was not checked |

When sources conflict, record the competing claims and their provenance. Do not
resolve a behavioral contradiction from prose preference. Route causal work to
`personal-evidence-debugging` when the user requests resolution.

## Architecture Guide

Select sections from the reader's decisions and the verified system boundary:

1. Purpose, scope, non-goals, and system boundary.
2. Entry points and the shortest useful mental model.
3. Major components, responsibilities, and ownership.
4. Control, data, state, and persistence flows.
5. Interfaces, schemas, events, external systems, and dependency direction.
6. Invariants, concurrency or ordering constraints, and lifecycle transitions.
7. Configuration, deployment, observability, failure, recovery, and security
   only to the depth supported by evidence and relevant to the reader.
8. Verified design decisions, tradeoffs, compatibility constraints, and known
   unknowns.
9. Source anchors, related documents, and the expected update path.

Do not force every section. A small library architecture guide may have no
deployment section. A data pipeline guide may need lineage and restart
semantics but not a broad API inventory.

Prefer a progressive reading path:

```text
purpose and boundary
  -> component map
  -> one representative flow
  -> component or contract details
  -> operations, failure, and tradeoffs
```

## API Or Reference Documentation

First distinguish the artifact:

- generated specification or reference;
- handwritten caller guide;
- internal implementation contract; or
- migration or compatibility guide.

For a caller-facing API, consider:

- stability and version scope;
- authentication and authorization when verified;
- endpoint, method, function, event, or schema identity;
- parameters, requiredness, defaults, units, and constraints;
- request, response, return, side effect, ordering, and idempotency behavior;
- error taxonomy and retry or recovery semantics;
- rate, size, timeout, or compatibility limits when supported; and
- minimal valid examples plus important boundary cases.

Keep generated inventories generated. Point readers to the generator and
canonical schema, and use handwritten prose for concepts, workflows, examples,
and non-obvious contracts. Do not hand-create an OpenAPI spec, generator,
linting pipeline, or hosted reference unless the user explicitly requests that
separate deliverable.

## Walkthrough Or Code Explanation

Choose a trace boundary before narrating:

```text
entry
  -> validation or normalization
  -> core transition or algorithm
  -> persistence or external effect
  -> response, cleanup, or failure
```

For each important step, connect:

- the responsible symbol;
- the incoming state or data;
- the transformation or decision;
- the produced state, output, or side effect; and
- the next boundary.

Explain patterns only when they help the reader predict behavior. State a
pattern's local benefit, cost, and alternative only when the code or design
evidence supports that interpretation. Avoid line-by-line paraphrase when a
short mental model and a few decisive anchors are enough.

## Tutorial Or Onboarding

Define a measurable outcome such as “run the local service and submit one
request” or “add one handler and verify it,” not merely “understand the system.”

Include the relevant subset of:

1. What the reader will accomplish.
2. Required knowledge, access, tools, environment, and starting state.
3. A preview of the final observable result.
4. Dependency-ordered concepts and actions.
5. Complete commands or edits with safe scopes.
6. Expected outputs or state after each material step.
7. Frequent checkpoints that stop error accumulation.
8. Plausible errors, their discriminating signals, and recovery or reset.
9. Cleanup for temporary state or resources.
10. A recap and one useful next path.

Verify commands in the environment that owns the tutorial when practical.
Record platform, version, environment, and material prerequisites when they
affect reproducibility. Never replace a missing verification with a fabricated
output. Do not promise a completion time without a reasonable basis.

## Visual Selection

| Relationship | Preferred form | Avoid when |
| --- | --- | --- |
| Exact field, flag, state, or component mappings | Table | Two mappings fit naturally in prose |
| Component, control, or data flow | Flowchart | The flow is a single obvious chain |
| Ordered interactions among participants | Sequence diagram | Timing and participant order do not matter |
| Lifecycle or valid transitions | State diagram | There is no meaningful state machine |
| Hierarchy or ownership | Tree | Nesting is shallow and already obvious |

Use real names in labels and keep the diagram small enough to audit. Describe
the important consequence in prose so the artifact remains useful when the
diagram cannot render. If one relationship is inferred, label it as inferred
both in the diagram and surrounding text.

## Final Artifact Check

After the last edit, verify:

- the artifact answers the stated reader goal at the intended depth;
- paths, symbols, identifiers, API names, configuration keys, and examples
  match current sources;
- executed commands and outputs are distinguished from illustrative material;
- claims about runtime, deployment, performance, security, rationale, and
  history do not exceed their evidence;
- generated ownership and source-of-truth links are correct;
- internal links and relevant external links resolve;
- diagrams agree with the prose and evidence;
- terminology is consistent without erasing exact project vocabulary;
- known unknowns and deliberately omitted sections are visible where needed;
  and
- the final diff contains no unrelated code, generator, CI, publication, or
  formatting expansion.
