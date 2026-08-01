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
provisional до `030-03`

## Summary
Превратить research probes в deterministic Windows regression suite для
entrypoints, wiring, bootstrap, verify, drift и Git safety.

## Provisional Acceptance
- Test suite запускается non-interactively на supported Windows environment.
- Matrix покрывает least-privilege default и заявленные fallbacks.
- Tests используют disposable workspaces и полный cleanup.
- Host-specific failures создают sanitized structured report.
- Linux release baseline включает platform-neutral contract tests.
- Документирован local two-host run и будущий Windows CI integration path.

## Depends On
- `040-01-add-windows-runtime-entrypoints`
- `040-02-add-windows-wiring-backend`
- `040-03-add-windows-verification-and-git-safety`

## Change Set
- none yet; перепланировать после `030-03`

## Verify
- Full Windows smoke на обоих hosts.
- Repeat run после cleanup.
- Linux release baseline и public-surface scans.

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `scripts/smoke-bootstrap-project.py`
- `scripts/smoke-verify-project.py`
- `scripts/smoke-wiring-discovery.py`

## Result
not started

## Next
- Mandatory refresh после `030-03`, затем выполнять после `040-03`.

## Log
- 2026-08-01T15:07:29Z provisional test card создана для обязательной Windows matrix.
