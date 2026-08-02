# Добавить automated native Windows smoke matrix

## Status
1.backlog

## Owner
ChangeRail core + operator

## OpenSpec Stage
story

## Series
`040-native-windows-implementation`

## Series Index
`04`

## Planning State
refreshed after `030-03`; pending deliver-ready decomposition

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
- none yet; run `$changerail-ff` after `040-03`

## Verify
- Full Windows smoke on both hosts or explicit blocker/caveat.
- Repeat run after cleanup.
- Linux release baseline and public-surface scans.

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `openspec/board/1.backlog/040-03-add-windows-verification-and-git-safety.md`
- `openspec/board/3.inprogress/030-03-freeze-native-windows-architecture.md`
- `scripts/smoke-bootstrap-project.py`
- `scripts/smoke-verify-project.py`
- `scripts/smoke-wiring-discovery.py`

## Result
refreshed; implementation not started

## Next
- После publish `040-03`: `$changerail-ff openspec/board/1.backlog/040-04-add-windows-automated-smoke.md`

## Log
- 2026-08-01T15:07:29Z provisional test card создана для обязательной Windows matrix.
- 2026-08-02T07:27:00Z refreshed against `030-03`: smoke must cover `.cmd`,
  generated-copy default, explicit fallbacks, cleanup and Git safety.
