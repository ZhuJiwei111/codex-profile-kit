---
name: ask-matt
description: Manual only. Select a Matt Pocock skill or engineering workflow when the user invokes ask-matt.
---

# Ask Matt

Recommend the smallest useful entry for the user's requested outcome. A focused
question or change may need no skill. Do not turn routing into an interview,
implementation, or a mandatory idea-to-shipping sequence.

## Choose an entry

| User outcome | Entry |
| --- | --- |
| Stress-test a plan or consequential requirement | `grilling` |
| Interview and maintain requested glossary/ADRs | `grilling` + `domain-modeling` |
| Resolve a large, uncertain design across sessions | `wayfinder` |
| Build an agreed specification | `to-spec` |
| Split a specification into dependency-aware work items | `to-tickets` |
| Implement an agreed work item | `implement` |
| Develop a concrete behavior test-first | `tdd` |
| Review a diff against requirements and standards | `code-review` |
| Diagnose a difficult bug with a reproducible signal | `personal-evidence-debugging` |
| Prepare incoming reports for implementation | `triage` |
| Explore structural improvements | `improve-codebase-architecture` |
| Design a module interface or seam | `codebase-design` |
| Clarify domain terminology or record an architectural decision | `domain-modeling` |
| Test one design question with throwaway code | `prototype` |
| Produce a cited research note or delegate reading | `research` |
| Prepare questions that another person must answer | `to-questionnaire` |
| Prepare a portable handoff for a real context or owner change | `handoff` |
| Guide steps only a human can perform | `wizard` |
| Teach a concept over multiple sessions | `teach` |
| Write instructions consumed by agents | `writing-for-agents` |
| Configure an issue tracker and domain-doc conventions | `setup-matt-pocock-skills` |

Choose one primary entry; add another only when the outcome requires it.
Read the selected installed `SKILL.md` before following it. Names in this table
are references, not native slash commands or a promise that a Skill tool exists.

Use the repository's existing terminology, issue tracker, and document owners.
Setup is needed only when a selected workflow actually lacks required project
configuration. Continue related work in the same chat unless a real handoff is
needed. Read [PHASE-BOUNDARIES.md](PHASE-BOUNDARIES.md) only when the user needs
the detailed upstream handoff decision tree; repository continuity rules win.
