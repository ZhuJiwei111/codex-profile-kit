# Source Notes

Checked: 2026-07-11.

The pre-revision local skill closely tracked the distinctive sequence and
wording of Matt Pocock's `grill-me` / `grilling` workflow: walk the design tree,
resolve decisions one at a time, provide a recommendation, and research
codebase facts before asking. This file records that upstream provenance and the
deliberate local adaptations.

## Sources

| Source | Pin or version | License/status | Role |
| --- | --- | --- | --- |
| [`grill-me`](https://github.com/mattpocock/skills/blob/v1.1.0/skills/productivity/grill-me/SKILL.md) | Annotated tag object `eabea89380927aadb93abf6e290a19334d249292`; commit `d574778f94cf620fcc8ce741584093bc650a61d3` | MIT, Copyright (c) 2026 Matt Pocock | Manual user-invoked entry point |
| [`grilling`](https://github.com/mattpocock/skills/blob/v1.1.0/skills/productivity/grilling/SKILL.md) | v1.1.0 at the same commit | MIT | Reusable one-question-at-a-time interview loop, recommendations, facts-versus-decisions split, and confirmation gate |
| [v1.1.0 release](https://github.com/mattpocock/skills/releases/tag/v1.1.0) | Released 2026-07-08 | Verified GitHub release | Evidence for the hardened confirmation gate and facts-versus-decisions behavior |
| [Question limits](https://github.com/mattpocock/skills/blob/v1.1.0/.out-of-scope/question-limits.md) | v1.1.0 | MIT | No numeric question cap; redundant questions are a prompt-quality problem rather than a counting problem |
| Local `personal-brainstorms` | Accepted local revision checked 2026-07-11 | Personal profile skill | Scope decomposition, alternatives, shared decision state, design synthesis, and downstream authorization handoff |

## Adopted

- Keep the public skill manual-only.
- Research discoverable facts before questioning the user.
- Put admitted material decisions to the user rather than answering them on the
  user's behalf.
- Ask one decision at a time, wait for feedback, and provide a recommendation
  with its material tradeoff.
- Stop based on shared understanding and resolved blockers, not a numeric
  question limit.
- Keep a confirmation gate before downstream work unless the invoking request
  already preauthorized planning after every blocker is locked.

## Deliberately Rejected

- A separate local `/grilling` slash command or a second workflow skill.
- Treating every possible branch as material to the current delivery slice.
- Using the leading word "relentless" to justify redundant, theatrical, or
  low-value questions.
- Letting the interviewer enact a plan before its gate is released.
- Requiring a redundant confirmation after the user explicitly preauthorized
  same-turn planning at the start of the session.

## Local Deviations

- One Codex skill combines the upstream manual entry point and reusable loop;
  `policy.allow_implicit_invocation: false` preserves the manual boundary.
- `personal-grilling` collaborates with `personal-brainstorms` only when both
  are explicitly invoked. Brainstorming coordinates design; grilling owns
  question admission, answer lockability, and blocking state.
- A question-admission gate filters discoverable facts, deferred decisions, and
  non-material implementation details before they reach the user.
- Non-material, low-risk, reversible details may be recorded as explicit
  assumptions. Material product or design decisions remain user-owned.
- Requirements briefs use Chinese headings by default and may release directly
  into the locally appropriate planning workflow when preauthorized.

## License Notice

MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
