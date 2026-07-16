# Source Notes

- skill: personal-prompt-optimizer
- checked_at: 2026-07-16
- source_classification: hybrid
- provenance_status: complete
- primary source: https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6 (official live guide; checked 2026-07-16)
- primary source: local user-locked decisions for manual invocation, two modes, authority boundaries, output shape, evidence levels, and owner routing
- local motivation: complex prompts tend to become more contradictory as patches accumulate; side-task discussions need a clean executable handoff
- adopted: outcome-first structure; simplify one coherent instruction group at a time; preserve success and stop conditions; centralize authorization; separate evidence from inference; compare the same representative case when evaluating runtime behavior
- rejected: a universal template; whole-stack rewrite by default; static claims of improvement; automatic triggering or persistence; copying the complete official guide
- local deviations: emit one canonical output; isolate it in a `text` block; remain manual-only; use the exact evidence labels `static_only`, `trace_based`, and `runtime_tested`
- runtime_dependency: none for the generic workflow; use `openai-docs` only for dynamic model or product facts
- derivation: conceptual adoption plus an original local workflow; no large passage copied from the source
- update_owner: maintainer of `personal-prompt-optimizer`
- update_rule: recheck the official guide and local owner boundaries when target surfaces, evidence semantics, output contract, or routing change
- provenance_gaps: none

```yaml
skill_admission:
  skill: personal-prompt-optimizer
  acquisition_mode: created
  source_classification: hybrid
  provenance_status: complete
  admission_status: admitted
  portability_disposition: internalized
  safety_status: passed
  safety_review: "static_pass: Static instruction and executable-surface review found no scripts, network, file-write, hook, MCP, credential, publication, or destructive-action surface."
  trigger_status: passed
  trigger_review: "product_pass: Product-confirmed in a fresh side-conversation: explicit discovery and manual Handoff Mode invocation."
  validation_status: passed
  validation:
    - "static_pass: quick_validate: active and portable snapshots passed on 2026-07-16"
    - "static_pass: profile tests: passed on 2026-07-16"
    - "static_pass: sync audit: zero drift on 2026-07-16"
    - "product_pass: product smoke: product-confirmed explicit discovery and manual Handoff Mode in a fresh side-conversation"
  update_owner: "maintainer of personal-prompt-optimizer"
  update_rule: "Repeat admission review when the source, trigger, safety boundary, owner routing, or runtime surface changes."
  rollback_basis: "Remove the skill from active discovery and the portable snapshot through the owning lifecycle workflow; reconstruct from the reviewed profile revision."
  unknowns_disposition: bounded-nonmaterial
  unknowns:
    - "Downstream prompt effectiveness is not runtime_tested."
    - "Negative no-invocation product smoke was not rerun."
```
