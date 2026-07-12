## Why

The rename is not operationally complete until the existing local consumer
projects stop using `/opt/opsx`, `/opsx:*`, `$opsx-*` and `bin/opsx-*`. The
known consumer list is machine-local and must stay out of tracked public docs.

## What Changes

- Add an operator-run migration step for the known local consumer set after the
  ChangeRail repository rename and bootstrap/verify updates are available.
- Add an explicit stop-gate: do not start known consumer migration until the
  operator has renamed the GitHub repository to `changerail` and local `origin`
  points to the new repository URL.
- Migrate one consumer project at a time, with active agent sessions stopped or
  finished before rewiring when possible.
- Update each consumer's `.claude`, `.codex`, `bin`, `AGENTS.md`, `CLAUDE.md`,
  `.mcp.json`, `.codex/config.toml` and local runbooks as needed.
- Verify each migrated consumer with `/opt/changerail/bin/verify-project
  <project>`.
- If active sessions cannot be stopped immediately, record the partial migration
  and create a separate follow-up board card for session restart and
  project-local commit/push work.
- Keep real consumer names, paths, migration notes and runtime evidence in
  ignored operator inventory or the consumer repositories themselves.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-project-verification`: require migrated known consumers to pass the
  ChangeRail consumer verification gate.
- `changerail-wiring-discovery`: require stale OPSX command/skill wiring to be removed
  from migrated consumers.

## Impact

- Ignored local operator inventory under `internal/`.
- Project-local files in the selected consumer repositories.
- No tracked public ChangeRail files should contain the real consumer project
  names or paths.
