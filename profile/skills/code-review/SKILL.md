---
name: code-review
description: Review uncommitted changes, a commit range, a branch, or a PR against documented standards and the requested behavior. Use for code review or review since a named base; report actionable findings with source evidence.
---

Review the user's selected changes along two axes:

- **Standards** — does the code conform to this repo's documented coding standards?
- **Spec** — does the code faithfully implement the originating issue / spec?

The main agent owns scope, synthesis, and the final verdict. Review is read-only;
it does not authorize fixes, tracker setup, Git writes, or external comments.
Use independent subagents only when the user or applicable repository
instructions authorize delegation and it materially helps this review. Otherwise
perform both axes in the main task.

## Process

### 1. Resolve the review surface

Use the request and `git status --short` to identify the target:

- **Uncommitted work:** inspect both `git diff --cached` and `git diff` so staged
  and unstaged changes are covered. When HEAD exists, `git diff HEAD` also shows
  their net effect. List untracked paths with `git ls-files --others
  --exclude-standard` and read relevant new source files separately; ordinary
  diffs omit them. Respect credential and unrelated-file boundaries.
- **Commit or explicit range:** resolve the named revisions and compare the
  requested endpoints. For one commit, inspect its patch with `git show`.
- **Branch relative to a base:** use `git diff <base>...HEAD` against the
  merge-base and `git log <base>..HEAD --oneline` for intent. This excludes local
  uncommitted work; include that work only when it belongs to the request.
- **PR:** use its verified base and head or the current PR diff through the
  available read interface. A local checkout must match those revisions before
  it can stand in for the PR.

Ask only when unresolved scope changes which work will be reviewed. If the
request clearly targets local edits, do not require a separate base choice.
Report invalid references or an empty selected surface directly; do not expand
to unrelated changes just to produce findings.

### 2. Identify the spec source

Look for the originating spec, in this order:

1. The user's current requirements, linked issue, or supplied spec path. Use an
   existing tracker workflow when available; a missing tracker file does not
   require setup.
2. Issue references in relevant commit messages (`#123`, `Closes #45`, etc.).
3. A spec file under `docs/`, `specs/`, or `.scratch/` matching the branch name or feature.
4. If no spec is available, continue correctness and standards review. Label
   requirement coverage as unverified; ask only when a missing requirement
   prevents judging a material behavior. Do not invent requirements.

### 3. Identify the standards sources

Anything in the repo that documents how code should be written, such as `CODING_STANDARDS.md` or `CONTRIBUTING.md`.

On top of whatever the repo documents, the Standards axis always carries the **smell baseline** below — a fixed set of Fowler code smells (_Refactoring_, ch.3) that applies even when a repo documents nothing. Two rules bind it:

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation — and, like any standard here, skip anything tooling already enforces.

Each smell reads *what it is* → *how to fix*; match it against the diff:

- **Mysterious Name** — a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code** — the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
- **Feature Envy** — a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps** — the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession** — a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches** — the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery** — one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change** — one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality** — abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains** — long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man** — a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest** — a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

### 4. Review the evidence

Use the following briefs inline or, when delegation is authorized, give each
bounded worker the selected diff, relevant new files, scope, and evidence.
Follow `personal-subagent-boundaries` for any workers.

**Standards sub-agent prompt** — include:

- The full diff command and commit list.
- The list of standards-source files you found in step 3, **plus the smell baseline from step 3** pasted in full — the sub-agent has no other access to it.
- The brief: "Report — per file/hunk where relevant — (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any baseline smell you spot: name it and quote the hunk. Distinguish hard violations from judgement calls — documented-standard breaches can be hard, but baseline smells are always judgement calls, and a documented repo standard overrides the baseline. Skip anything tooling enforces. Under 400 words."

**Spec sub-agent prompt** — include:

- The diff command and commit list.
- The path or fetched contents of the spec.
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Under 400 words."

If the spec is missing, skip that requirements comparison and note the limit.

### 5. Aggregate

Verify candidate findings against the actual selected changes, remove duplicate
or unsupported findings, and prioritize by consequence. Keep standards and
requirements provenance visible where it explains the issue, but produce one
coherent verdict. Each actionable finding needs a location, realistic trigger,
impact, and supporting evidence. Separate optional design preferences from bugs.

Report what was reviewed and material verification limits. If no actionable
issue remains, say so without inventing findings or treating missing evidence
as proof of correctness.

## Why two axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's conventions → **Spec pass, Standards fail.**

Preserving both sources of evidence prevents one axis from masking the other;
the main agent still owns prioritization and the final verdict.
