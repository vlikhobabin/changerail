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
provisional до `030-03`

## Summary
Реализовать выбранный Windows backend для directory/file wiring в bootstrap и
discovery, включая least-privilege default и явно ограниченные fallbacks.

## Provisional Acceptance
- Bootstrap выбирает strategy детерминированно по support contract.
- Default не требует elevation, если architecture research подтвердил viable
  least-privilege path.
- Directory и file wiring обрабатываются раздельно.
- Partial failure откатывает только созданные текущим run artifacts.
- Dry-run точно показывает выбранный backend и tracked/generated ownership.
- Upgrade повторяем и не перетирает project-owned files.

## Depends On
- `040-01-add-windows-runtime-entrypoints`
- `030-03-freeze-native-windows-architecture`

## Change Set
- none yet; перепланировать после `030-03`

## Verify
- Windows bootstrap positive/negative fixtures.
- Non-elevated live smoke на обоих hosts.
- POSIX bootstrap regression.

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `bin/bootstrap-project`
- `scripts/smoke-wiring-discovery.py`

## Result
not started

## Next
- Mandatory refresh после `030-03`, затем выполнять после `040-01`.

## Log
- 2026-08-01T15:07:29Z provisional card создана из symlink privilege report.
