---
name: personal-branch-finish
description: Use when implementation is complete and verified, and the remaining work is summarizing changes, deciding commit or PR readiness, or preparing a clean handoff.
---

# Personal Branch Finish

Finish with evidence and a clean handoff.

## Checklist

- Inspect changed files and make sure they match the request.
- Confirm verification commands and outcomes.
- Note skipped checks and residual risk.
- Keep unrelated user changes out of summaries, commits, and staging.
- If asked to commit, stage intentionally and use a concise factual message.
- If asked to open a PR, include summary, tests, and known risks.
- After the summary, include 1-3 concrete next commands or prompts only when
  they directly continue the task, such as broader tests, commit, PR, output
  inspection, or starting a new conversation to analyze completed results.

## Do Not

- Claim work is complete before verification.
- Create commits or PRs unless the user asked.
- Revert unrelated files to make the branch look clean.
- Leave long-running sessions active when the task is done.
- Add next steps when there is no natural follow-up, the user only asked for a
  direct result, or the task is too small to need one.
- End with generic open-ended phrasing such as "If you want...".
