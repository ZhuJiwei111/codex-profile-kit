---
name: code-simplifier
description: Use when simplifying recently modified code for clarity, consistency, and maintainability while preserving exact behavior.
metadata:
  sources:
    - https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-simplifier
---

# Code Simplifier

## Scope

Simplify code that was recently modified or explicitly selected by the user. The goal is clearer code with identical behavior.

## Boundaries

Use these instead when appropriate:

- `test-driven-development`: adding features, bug fixes, or behavior changes.
- `systematic-debugging`: investigating failures or unexpected behavior.
- `receiving-code-review`: evaluating review feedback.
- `verification-before-completion`: final evidence before claiming completion.

## Rules

1. Preserve behavior exactly.
2. Prefer local, low-risk simplifications.
3. Follow existing project style over generic preferences.
4. Remove unnecessary abstraction only when it reduces real complexity.
5. Do not expand scope beyond recently touched or user-selected code without asking.

## Good Simplifications

- Improve names that obscure intent.
- Flatten avoidable nesting.
- Remove duplicate branches or dead code.
- Replace clever expressions with explicit flow.
- Consolidate repeated local logic when it clarifies ownership.
- Remove comments that restate obvious code; keep comments that explain non-obvious constraints.

## Avoid

- Behavior changes disguised as cleanup.
- Broad refactors unrelated to the touched code.
- Dense one-liners, nested ternaries, or clever abstractions.
- Reformatting churn without clarity benefit.
- Removing helpful structure just to reduce line count.

## Verification

After simplification, run the narrowest meaningful verification available. If no tests exist, use static checks, build commands, or targeted manual inspection and say what was not verified.

## Common Mistakes

| Mistake | Correction |
|---|---|
| "Simpler" means fewer lines | Simpler means easier to understand and maintain. |
| Refactoring across the repo | Stay near recent changes unless requested. |
| Trusting visual equivalence | Run verification or state the gap. |
| Applying personal style | Follow the repository's established style. |
