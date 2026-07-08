## Why

OPSX bootstrap needs a deterministic gate that fails when a consumer project is
not actually wired to the OPSX source of truth. Without a red/green verifier,
bootstrap and future adoption flows can silently drift.

## What Changes

- Add executable `bin/verify-project`.
- Verify consumer project symlink-и, OpenSpec config, MCP/Codex scope,
  helper/schema reachability and ignored runtime/auth paths.
- Support direct `/opt/opsx` wiring and documented aggregator paths.
- Return meaningful exit codes and concise check output.

## Capabilities

### New Capabilities
- `opsx-project-verification`: red/green verification gate for OPSX consumer
  projects.

### Modified Capabilities
- none

## Impact

- Affected files: `bin/verify-project`, `scripts/**` if shared helper code is
  useful, `docs/**`, `README.md`, `openspec/specs/**`.
- Consumer projects can be checked before adoption, after bootstrap and before
  publish.
- Verification reads project files but must not write runtime/auth state into
  tracked files.
