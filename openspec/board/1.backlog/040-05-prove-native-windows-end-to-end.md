# Доказать native Windows support end-to-end

## Status
1.backlog

## Owner
ChangeRail core + operator

## OpenSpec Stage
story

## Series
`040-native-windows-implementation`

## Series Index
`05`

## Planning State
provisional до `030-03`

## Summary
На обоих Windows hosts пройти clean-clone consumer lifecycle: runtime setup,
bootstrap, verify, skill discovery, scoped no-push delivery smoke, update/drift
check и повторную verification.

## Provisional Acceptance
- Оба hosts начинают из clean disposable clone без ручной правки source files.
- Bootstrap и verify проходят в заявленном non-elevated default mode.
- Agent skill/command discovery подтверждает required Windows surfaces.
- Scoped delivery smoke не затрагивает unrelated/runtime files и не требует
  публикации в реальный remote.
- ChangeRail update сохраняет wiring contract или дает documented migration.
- Final compatibility matrix и migration guide основаны на retained evidence.
- Linux release baseline остается green.

## Depends On
- `040-04-add-windows-automated-smoke`
- Серия `020-one-command-delivery-experience` завершена.

## Change Set
- none yet; перепланировать после `030-03`

## Verify
- Two-host end-to-end report с sanitized evidence.
- Windows smoke matrix.
- Full Linux release baseline и public-surface current/history scans.

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `docs/compatibility.md`
- `docs/migration-guide.md`
- `docs/consumer-adoption-runbook.md`

## Result
not started

## Next
- Mandatory refresh после `030-03`; выполнять последней в серии `040`.

## Log
- 2026-08-01T15:07:29Z provisional exit-gate card создана для двух Windows hosts.
