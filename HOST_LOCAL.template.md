# Host-Local Codex Facts

This file is local-only, read-only input for ordinary tasks and monitoring.
Never store credentials, tokens, private-key contents, secret-bearing proxy
commands, authentication sockets, or session state here. Updating this file
requires separate configuration authority; a monitoring request alone does not
authorize edits.

## Host Identity

- Updated at (ISO 8601 with timezone):
- Operating system and version:
- Architecture:
- Codex controller host ID or label:
- Codex home:
- Long-lived profile repository:

## Python And Package Policy

- Ordinary Python environment:
- Absolute Python interpreter:
- Conda or Mamba root:
- Reusable project-environment policy:
- Standing package-install authority, if any:

## Codex Installation

- Codex desktop version:
- Codex CLI version and absolute executable:
- Hook runtime interpreter:
- Known runtime or plugin-cache paths that must not be modified:
- Fresh-task hook trust status and verification date:

## Local Resources

- Storage locations and material capacity constraints:
- CPU, memory, GPU, or power constraints relevant to task planning:
- Sleep or availability constraints for local Scheduled tasks:

## Network And Remote Aliases

Record aliases and non-secret route facts only. Keep SSH configuration
authoritative; do not copy secrets from it.

- Proxy or route aliases:
- SSH aliases, effective non-secret endpoint facts, and last bounded probe:
- Saved project roots by host ID or project label:
- Known connectivity limitations:

## Host-Specific Decisions

- Approved local installation or deployment conventions:
- Paths or services that require explicit approval:
- Other current, non-secret host limitations:

## File Protection

- POSIX: owner-readable and owner-writable only (`0600`).
- Windows: remove inherited access where appropriate and grant read/write only
  to the current user and required system administrators; record the exact ACL
  verification command used.
