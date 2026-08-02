# Добавить automated native Windows smoke matrix

## Status
2.todo

## Owner
ChangeRail core + operator

## OpenSpec Stage
story

## Series
`040-native-windows-implementation`

## Series Index
`04`

## Planning State
deliver-ready after `030` exit audit; OpenSpec artifacts deferred to internal
`ff` during `$chrl-deliver`

## Source
- `030-03-freeze-native-windows-architecture`
- `040-01-add-windows-runtime-entrypoints`
- `040-02-add-windows-wiring-backend`
- `040-03-add-windows-verification-and-git-safety`

## Summary
Превратить research probes в deterministic Windows regression suite for `.cmd`
entrypoints, generated wiring, verifier/drift, Git safety, cleanup and
fallback behavior.

## Acceptance
- Test suite runs non-interactively on supported native Windows environments.
- Deterministic local fixtures cover `.cmd` launch, generated copy ownership,
  stale copy detection, explicit refresh, project-owned divergence, cleanup,
  Git status/add/index behavior, spaces and non-ASCII paths.
- Live matrix covers both `windows-host-a` and `windows-host-b`, or records an
  explicit blocker/caveat before claiming host coverage.
- Matrix covers generated-copy default and bounded symlink/junction fallback
  negative/positive conditions.
- Tests use disposable workspaces and idempotent cleanup.
- Host-specific failures create sanitized structured report under ignored
  runtime state.
- Linux release baseline includes platform-neutral contract tests.
- Local two-host run and future Windows CI integration path are documented.

## Depends On
- `040-01-add-windows-runtime-entrypoints`
- `040-02-add-windows-wiring-backend`
- `040-03-add-windows-verification-and-git-safety`

## Change Set
- `openspec/changes/add-windows-smoke-matrix-runner/` (planned)
- `openspec/changes/document-windows-smoke-operations/` (planned)

## Verify
- Full Windows smoke on both hosts or explicit blocker/caveat.
- Repeat run after cleanup.
- Linux release baseline and public-surface scans.

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `openspec/board/2.todo/040-03-add-windows-verification-and-git-safety.md`
- `openspec/board/4.done/030-03-freeze-native-windows-architecture.md`
- `scripts/smoke-bootstrap-project.py`
- `scripts/smoke-verify-project.py`
- `scripts/smoke-wiring-discovery.py`

## Change 1: `add-windows-smoke-matrix-runner`

### Why
Research probes must become deterministic regression coverage that can be
rerun non-interactively on native Windows hosts.

### Goal
Add a Windows smoke matrix runner for entrypoints, generated wiring,
verification, drift, Git safety, cleanup and fallback behavior.

### Acceptance
- Matrix runs non-interactively against `windows-host-a` and `windows-host-b`.
- Reports are sanitized and retained only under ignored runtime state.
- Fixtures use disposable workspaces and idempotent cleanup.

### Depends On
- `040-01-add-windows-runtime-entrypoints`
- `040-02-add-windows-wiring-backend`
- `040-03-add-windows-verification-and-git-safety`

### Related
- `openspec/changes/add-windows-smoke-matrix-runner/`

## Change 2: `document-windows-smoke-operations`

### Why
Operators need a repeatable local two-host workflow and a clear future CI path
without exposing private SSH details.

### Goal
Document how to run, interpret and retain Windows smoke evidence, including
explicit blocker/caveat handling.

### Acceptance
- Docs describe local two-host execution and sanitized evidence retention.
- Future Windows CI integration path is documented.
- Linux release baseline includes platform-neutral contract tests.

### Depends On
- `add-windows-smoke-matrix-runner`

### Related
- `openspec/changes/document-windows-smoke-operations/`

## Result
ready for `$chrl-deliver`

## Next
- Выполнять после `040-03` в tracked runner plan
  `040-native-windows-implementation`.

## Log
- 2026-08-01T15:07:29Z provisional test card создана для обязательной Windows matrix.
- 2026-08-02T07:27:00Z refreshed against `030-03`: smoke must cover `.cmd`,
  generated-copy default, explicit fallbacks, cleanup and Git safety.
- 2026-08-02T08:24:42Z переведена в `2.todo` после exit audit `030`; planned
  changes записаны, artifacts будут созданы internal `ff` phase.
