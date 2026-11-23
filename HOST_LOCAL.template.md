# Host-Local Codex Facts

Local-only, non-secret host paths and standing policy. Ordinary tasks read this
file when relevant; updates require configuration authority. Project connections
and live execution state belong to their project registration or native tools.
Do not copy credentials, auth/session state, SSH parameters, process status,
capacity snapshots or old verification results here.

## Paths

- Codex home:
- Portable profile source:
- Host Python interpreter and environment:
- Conda/Mamba root, if used:
- Codex desktop application:
- Codex CLI executable or discovery method:

## Standing Policy

- Authorized ordinary package installation scope:
- Environment/channel conventions:
- Host-specific resource or availability constraints:
- Protected local paths:

Verify volatile versions and availability from the actual runtime when needed.
Record tests and deployment events in their owning journal, not in this file.
Project SSH and model routing remain in project/platform configuration.

## File Protection

POSIX mode 0600; on Windows restrict access to the user and required system
administrators. This file is not a credential store.
