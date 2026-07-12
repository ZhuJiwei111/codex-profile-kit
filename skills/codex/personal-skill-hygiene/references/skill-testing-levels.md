# Risk-Scaled Skill Testing

Scale testing to what the change can get wrong. Do not impose a universal ritual
on every metadata or documentation edit.

## Levels

| Change or decision | Minimum evidence |
| --- | --- |
| Metadata, links, or mechanical structure | Frontmatter/schema validation, resource-link check, and stale-name search |
| Trigger or scope wording | One positive trigger, one negative trigger, and one adjacent-skill conflict scenario |
| Technique or reusable pattern | Application case, variation case, and missing-information case |
| Discipline, safety, or destructive guidance | Baseline behavior without the new guidance when feasible, combined-pressure scenarios, captured rationalizations, and re-test after revision |
| Plugin, hook, external integration, credentials, or trust | Dedicated validator or dry-run plus the product's approval/trust mechanism; never expose secrets |

Broaden testing when the artifact can silently trigger too often, suppress a
needed workflow, delete the only copy, bypass trust, or cause external effects.

## Trigger Probes

Keep prompts natural and withhold the intended routing answer from an
independent evaluator.

- Positive: the target's lifecycle state or disposition is the central
  decision.
- Negative: the request mentions a skill/plugin/hook but does not ask for its
  lifecycle.
- Adjacent: a specialist skill should clearly own authoring, installation, hook
  design, profile audit, or standalone MCP configuration.

Record the prompt, observed owner, whether hygiene remained bounded, and any
unexpected overlap. A passing answer should name unknown state instead of
manufacturing certainty.

## Pressure Tests

For safety or cleanup rules, combine plausible pressures such as:

- a deadline plus a large cache;
- an obsolete artifact plus an unverified replacement;
- an apparent backup plus no restore check;
- a user request for cleanup plus local modifications of unknown provenance;
- a hook definition change plus pressure to bypass re-trust.

Capture the shortcuts an evaluator tries to justify. Turn recurring failures
into explicit boundaries, then repeat the smallest scenario that exposed them.

## Proportionality

- Do not require five or more repetitions for every change.
- Do not delete and recreate a healthy skill merely to prove edit discipline.
- Do not require commits, pushes, publication, or production mutations as test
  evidence.
- Do not copy Claude-specific plugin, hook, or invocation assumptions into
  Codex workflows.
- Prefer isolated or read-only probes when live-state changes are unnecessary.
- Treat validation success as evidence for the tested behavior only, not proof
  of installation, enablement, trust, or whole-profile health.
