# Добавить Windows verification, drift и Git safety

## Status
1.backlog

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`040-native-windows-implementation`

## Series Index
`03`

## Planning State
provisional до `030-03`

## Summary
Научить verifier и drift gate распознавать выбранный Windows wiring backend и
fail-closed блокировать случайное добавление ChangeRail source в consumer Git.

## Provisional Acceptance
- `verify-project` отличает valid Windows wiring от copied drift и ordinary dir.
- Git safety check доказывает, что wiring targets не попадают в staging plan.
- Junction/symlink/generated-copy semantics соответствуют решению `030-03`.
- Copy fallback разрешен только при explicit profile и имеет source pin/drift
  evidence.
- Ignore rules минимальны и не скрывают project-owned source.
- Rename/update/uninstall scenarios покрыты negative tests.

## Depends On
- `040-02-add-windows-wiring-backend`
- `010-05-add-verification-profiles-and-severity`

## Change Set
- none yet; перепланировать после `030-03`

## Verify
- Git index/status fixtures на Windows.
- `verify-project` и drift smoke на обоих hosts.
- Linux verification regressions и public-surface scan.

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `bin/verify-project`
- `scripts/smoke-drift.py`

## Result
not started

## Next
- Mandatory refresh после `030-03`, затем выполнять после `040-02`.

## Log
- 2026-08-01T15:07:29Z provisional card создана из Git junction report.
