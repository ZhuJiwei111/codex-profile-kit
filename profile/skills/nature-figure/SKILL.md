---
name: nature-figure
description: "Create, revise, audit, and export manuscript scientific figures in Python or R. Use for 论文配图、科研绘图、多面板图 and submission-ready plots, or explicitly requested AI-generated graphical abstracts and mechanism schematics. Not for interactive dashboards, data cleaning, or statistics-only analysis."
---

# Nature Figure Making — Router

This skill is split into two layers:

- A **static layer** under `static/` that holds versioned, reusable content fragments (the figure contract and default stance, plus a per-backend quick-start for Python and R).
- A **dynamic layer** (this file plus `manifest.yaml`) that detects the plotting backend and loads only the fragment needed for the current job. The large design, API, pattern, and QA material lives in on-demand references.

Do not try to apply the figure logic from memory or from this router. Always load fragments from disk as described below.

## Routing protocol

Follow these steps every time the skill is invoked.

### 0. Check for the OpenRouter AI-schematic route

For a generic AI-generated illustration or graphical abstract, use the installed native imagegen workflow when available; do not switch providers implicitly. The OpenRouter route below applies only when the user explicitly names OpenRouter and authorizes that provider request or asks for its reproducible payload. Do **not** ask "Python or R?" for this non-plotting route.

For this route:

1. Read [manifest.yaml](manifest.yaml) and the `always_load` files.
2. Read [references/openrouter-image-generation.md](references/openrouter-image-generation.md).
3. Use [scripts/generate_openrouter_schematic.py](scripts/generate_openrouter_schematic.py) when the user wants a real API call or a reproducible payload.
4. Treat output as a draft schematic / graphical abstract, not as a quantitative data panel. Do not invent experimental values, author logos, institutional marks, or unsupported mechanisms.

Only continue to the Python/R backend gate for plotting, charting, data visualization, or manuscript figure assembly tasks that are not explicit OpenRouter AI image-generation requests.

### 1. Load the manifest and the core layer

Read [manifest.yaml](manifest.yaml). It declares the `backend` axis, the allowed values, and the file paths each value maps to.

Also read every file listed under `always_load` (`static/core/contract.md` and `static/core/stance.md`). These hold the figure contract, the backend gate, the missing-runtime rule, the privacy rule, and the default operating stance that apply to every figure job.

### 2. Resolve the plotting backend

Honor an explicit Python/R choice, language-specific input, or established
project workflow. Otherwise read an already-saved preference with
`scripts/nature_figure_backend.py get`; reading it does not authorize changing it.
If no preference exists, use the project's installed plotting stack, normally
Python/matplotlib when it is already available. Ask only when the choice changes
compatibility, reproducibility, requested editability, or dependency cost.
Save a new persistent preference with the helper only when the user asks to
remember it. Keep the scientific drawing source in the selected backend;
normal image/PDF viewers and renderers may inspect its outputs.

### 3. Load the matching backend fragment

After the backend is resolved, Read the mapped fragment (`static/fragments/backend/python.md` or `static/fragments/backend/r.md`). It carries the backend-only execution rule and the publication quick-start (rcParams/theme and export helper). Do **not** load the other backend's fragment.

### 4. Build the figure using the loaded material

Apply the loaded material in this order:

1. Figure contract (`core/contract.md`) — write the core conclusion, map the evidence chain, classify the archetype, set the journal/export contract, before any code.
2. Default stance (`core/stance.md`) — archetype-first composition, hero panel, restrained palette, statistics/integrity as part of the figure.
3. Backend fragment — the exclusive Python or R quick-start and execution rule.
4. Template adaptation — when reusing bundled examples or user-provided plotting code, load `references/asset-adaptation.md` before mapping data or changing the script.
5. Delivery preflight — before final delivery, load `references/qa-contract.md`, run `scripts/validate_figure.py` on the plotting source, then inspect the rendered outputs at final size.

The chart serves the scientific logic; aesthetic polish is subordinate to making the core conclusion clear, defensible, and reviewable.

### 5. Reach for references only when needed

The files under `references/` are deep references, not defaults. Open them on demand per the `references.on_demand` table in the manifest — for example `references/figure-contract.md` to build the contract, `references/asset-adaptation.md` to reuse a plotting template safely, `references/template-catalog.md` for validated Python CSV templates, `references/api.md` for the Python palette and helpers, `references/r-workflow.md` for R, `references/design-theory.md` for color/typography/export rationale, `references/common-patterns.md` and `references/chart-types.md` for layout/chart recipes, `references/nature-2026-observations.md` for real Nature page archetypes, `references/qa-contract.md` before final delivery, and `references/tutorials.md` / `references/demos.md` for worked examples.

## Why this split

- The static layer is versioned and reviewable. The backend gate is now explicit in the manifest rather than buried in prose.
- The dynamic layer keeps each invocation cheap: only the selected backend's quick-start enters context, and the 2,600+ lines of reference depth load only when a step needs them.
- The router itself is short on purpose. Update fragments and references, not this file, when adding scope.
- This structure mirrors `nature-writing`, `nature-polishing`, `nature-reader`, and `nature-paper2ppt`.
