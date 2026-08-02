# Добавить native Windows wiring backend

## Status
1.backlog

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`040-native-windows-implementation`

## Series Index
`02`

## Planning State
refreshed after `030-03`; pending deliver-ready decomposition

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
- none yet; run `$changerail-ff` after `040-01`

## Verify
- Windows bootstrap positive and negative fixtures for generated default,
  symlink fallback, junction fallback and partial failure cleanup.
- Drift/refresh fixture for generated copies after ChangeRail source update.
- Live smoke on both Windows hosts or explicit blocker/caveat.
- POSIX bootstrap regression.

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `openspec/board/1.backlog/040-01-add-windows-runtime-entrypoints.md`
- `openspec/board/3.inprogress/030-03-freeze-native-windows-architecture.md`
- `bin/bootstrap-project`
- `scripts/smoke-wiring-discovery.py`

## Result
refreshed; implementation not started

## Next
- После publish `040-01`: `$changerail-ff openspec/board/1.backlog/040-02-add-windows-wiring-backend.md`

## Log
- 2026-08-01T15:07:29Z provisional card создана из symlink privilege report.
- 2026-08-02T07:27:00Z refreshed against `030-03`: generated-copy wiring is
  the native Windows default; symlink/junction are explicit bounded fallbacks.
