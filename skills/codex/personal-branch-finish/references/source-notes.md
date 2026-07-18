# Source Notes

Checked: 2026-07-18.

The design is informed by Superpowers v6.1.1
[`finishing-a-development-branch`](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/finishing-a-development-branch/SKILL.md)
at commit `d884ae04edebef577e82ff7c4e143debd0bbec99`, licensed MIT by Jesse Vincent,
and by the official Git documentation for `git add`, `git push`, and worktrees.

Local preferences are explicit Git outcomes, exact task-owned staging,
preservation of unrelated state, and direct non-force pushes to exact refs.
Only an end-to-end branch, commit, push, and draft-PR request routes to
`github:yeet`; branch finish itself supports handoff, commit, commit plus push,
and push only.
