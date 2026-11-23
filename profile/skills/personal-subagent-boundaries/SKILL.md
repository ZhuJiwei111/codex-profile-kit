---
name: personal-subagent-boundaries
description: Delegate bounded subagents or workers whose results return to the assigning task, including DS CLI execution workers and native independent GPT reviewers. Requests for 会话 or worker 会话 belong to personal-multiline-coordination, not this skill. Not for recurring monitoring.
---

# Personal Subagent Boundaries

## Choose The Delegation Form

Use this skill when the assigning task owns user interaction and acceptance,
and a worker returns a bounded result. This includes managed GPT subagents and
non-interactive model CLI runs, local or remote. A CLI session ID or
resume capability does not make the worker a user-owned conversation.

## Route The User's Request

- “派出会话”, “新建会话”, and “worker 会话” mean a user-owned interactive GPT
  App chat. Route to [personal-multiline-coordination](../personal-multiline-coordination/SKILL.md).
  The conversation requirement takes precedence over worker; a persistent CLI
  session is not an App chat. Do not ask again when the request settles the form.
- “派出 subagent” or “让 worker 做完交回” without a requested conversation means
  a bounded assignment. For execution work, prefer DS workers through the platform-configured CLI; native
  GPT subagents are also available when suited to the task and authorized tools.
- For requested independent review or discussion without a named model, prefer
  a native independent GPT subagent. “独立 GPT 审阅” uses that route unless the
  user also asks for a conversation. This does not turn ordinary discussion
  with the main task into permission to delegate.
- Honor explicitly requested DS, Claude, GPT, or reviewer combinations. Never
  add a panel by default. Choose local or remote execution from the task’s authoritative workspace and required tools, following project conventions. Use that host’s existing execution entrypoint; authentication and model configuration belong to the tool, not this skill. Do not hardcode model versions here or silently switch hosts after a failure. If the requested
  route is unavailable, report that limitation rather than silently substituting.

Delegate only when requested or when an independent bounded line materially
improves speed, isolation, or review quality within existing delegation authority.

## Assignment And Acceptance

Perform small mechanical work directly. The scope and evidence boundaries below
apply to every worker form selected through the routing rules above; selection
adds no trial, approval or reporting step.

Give the worker the smallest useful context: goal, concrete deliverable, actual
`cwd`, stable input or revision, read boundary, exclusive write boundary, stop
condition, and expected evidence. Use the minimum useful `fork_turns` or a
curated packet. Independent reviewers start with their own context and the necessary source
materials, without the implementer's reasoning or another reviewer's verdict.
Provide requirements and evidence, not a desired conclusion. For research assignments, use the [research handoff rules](../personal-research-project/references/collaboration.md) to distinguish current decisions from historical reference configurations. For cleanup assignments, pass the actual retention and deletion authority. Use
[personal-temporary-work](../personal-temporary-work/SKILL.md) only for task-created
scratch; existing project materials follow the assigned project scope. Unclear
deletion does not block other independently authorized work.

Use one writer for intersecting mutation surfaces. A worker returns unresolved choices or authority gaps to the assigning task;
it does not ask the user independently, expand authority, touch another surface,
perform unassigned Git or external actions, or start an unassigned later phase.
A blocked part does not stop independent work that remains within the assignment. User-authorized remote write surfaces
explicitly included in the assignment remain within scope; they do not authorize
publication, messages, credentials or unrelated remote operations. Persistent App tasks and monitoring belong to their separate workflows.
Worktree creation inherits the global creation-and-location confirmation rule;
worker dispatch does not supply that confirmation. Pass the confirmed working
directory to the worker; missing worktree decisions return to the assigning task.
For App-chat worktree setup, use the
[coordination workflow](../personal-multiline-coordination/SKILL.md#worktree-selection-and-creation).

The main task owns scope, decisions, user interaction, intake, synthesis, and
the final verdict. Evaluate worker evidence; do not vote by worker count or
repeat the entire assignment after a sufficient handoff.

At the stop condition, require the result, changed paths, checks or source
anchors, omissions, and uncertainty. Unexpected overlap or missing authority
returns to the main task. Delivering the result does not authorize deleting its
evidence or archiving user-owned App chats. Runtime handles, task-created scratch
and persistent conversation lifecycle are separate cleanup scopes.

## Execution And Observation

Managed subagents use their native result and wait tools. Authorized
non-interactive CLI commands long enough to need detached observation use
`personal-long-job-supervisor:supervise-long-jobs`; supervise the actual command,
not a loop watching a chat. The assigning task consumes the result and accepts
actual artifacts. Completion events and exit codes do not establish acceptance.
Platform skills own connection, environment and CLI adaptation; the supervisor
owns command observation. This skill owns the bounded assignment and handoff.

Read `references/source-notes.md` only when maintaining provenance.
