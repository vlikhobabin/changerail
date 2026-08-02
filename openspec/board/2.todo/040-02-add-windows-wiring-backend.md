# Добавить native Windows wiring backend

## Status
2.todo

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`040-native-windows-implementation`

## Series Index
`02`

## Planning State
deliver-ready after `030` exit audit; OpenSpec artifacts deferred to internal
`ff` during `$chrl-deliver`

## Source
- `030-03-freeze-native-windows-architecture`
- `040-01-add-windows-runtime-entrypoints`

## Summary
Реализовать generated project-local Windows wiring backend in bootstrap and
adoption/discovery surfaces, with explicit symlink and junction fallbacks.

## Acceptance
- Bootstrap chooses Windows generated-copy default deterministically by platform
  and project policy.
- Generated command, skill and helper wiring artifacts are owned by a manifest
  or tracked project policy with source identity, digest/refresh semantics and
  project-owned divergence handling.
- Default Windows path does not require Developer Mode, administrator elevation
  or symlink privileges.
- Directory and file wiring are classified separately.
- Symlink fallback requires explicit operator opt-in and positive
  privilege/Developer Mode proof.
- Junction fallback requires explicit operator opt-in, link-aware cleanup and
  Git-safety preconditions.
- Partial failure rolls back only artifacts created by the current run.
- Dry-run reports selected backend, generated ownership and fallback reasons.
- Upgrade/refresh updates only generated-owned files and never silently
  overwrites project-owned files.
- Existing POSIX symlink wiring remains compatible.

## Depends On
- `040-01-add-windows-runtime-entrypoints`
- `030-03-freeze-native-windows-architecture`

## Change Set
- `openspec/changes/add-windows-generated-wiring-backend/` (planned)
- `openspec/changes/add-windows-wiring-refresh-and-fallbacks/` (planned)

## Verify
- Windows bootstrap positive and negative fixtures for generated default,
  symlink fallback, junction fallback and partial failure cleanup.
- Drift/refresh fixture for generated copies after ChangeRail source update.
- Live smoke on both Windows hosts or explicit blocker/caveat.
- POSIX bootstrap regression.

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `openspec/board/2.todo/040-01-add-windows-runtime-entrypoints.md`
- `openspec/board/4.done/030-03-freeze-native-windows-architecture.md`
- `bin/bootstrap-project`
- `scripts/smoke-wiring-discovery.py`

## Change 1: `add-windows-generated-wiring-backend`

### Why
Windows needs a default wiring backend that works without Developer Mode,
administrator elevation or symlink privileges.

### Goal
Teach bootstrap/adoption surfaces to select generated project-local copies as
the native Windows default and record generated ownership deterministically.

### Acceptance
- Platform and project policy select the generated-copy backend on Windows.
- Generated artifacts include source identity, digest and refresh semantics.
- Dry-run reports backend choice and fallback reasons.

### Depends On
- `040-01-add-windows-runtime-entrypoints`

### Related
- `openspec/changes/add-windows-generated-wiring-backend/`

## Change 2: `add-windows-wiring-refresh-and-fallbacks`

### Why
Generated copies need safe refresh, rollback and bounded fallback semantics, and
link modes must stay explicit and fail-closed.

### Goal
Add refresh/upgrade, partial rollback, symlink opt-in and junction opt-in logic
that uses the same ownership classification as bootstrap.

### Acceptance
- Refresh updates only generated-owned artifacts.
- Partial failure cleanup removes only files created by the current run.
- Symlink and junction fallback require explicit opt-in and positive evidence.

### Depends On
- `add-windows-generated-wiring-backend`

### Related
- `openspec/changes/add-windows-wiring-refresh-and-fallbacks/`

## Result
ready for `$chrl-deliver`

## Next
- Выполнять после `040-01` в tracked runner plan
  `040-native-windows-implementation`.

## Log
- 2026-08-01T15:07:29Z provisional card создана из symlink privilege report.
- 2026-08-02T07:27:00Z refreshed against `030-03`: generated-copy wiring is
  the native Windows default; symlink/junction are explicit bounded fallbacks.
- 2026-08-02T08:24:42Z переведена в `2.todo` после exit audit `030`; planned
  changes записаны, artifacts будут созданы internal `ff` phase.
