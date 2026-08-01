# Серия 040: Реализация native Windows support

## Status
1.backlog

## Owner
ChangeRail core + operator

## OpenSpec Stage
epic

## Series
`040-native-windows-implementation`

## Series Index
`00`

## Planning State
provisional; mandatory refresh после серии `030`

## Delivery Mode
coordination-only; не запускать `$chrl-deliver` для этой epic-карточки

## Source
- Обязательное product решение о native Windows support.
- Candidate implementation outline до завершения research серии `030`.

## Summary
Реализовать выбранную в `030-03` native Windows architecture для entrypoints,
wiring, bootstrap, verification, Git safety и automated/end-to-end tests.

## Entry Gate
- Серия `030-native-windows-discovery` завершена.
- Architecture decision и test matrix приняты.
- Эта epic и все series cards переписаны против фактических research results.
- До выполнения gate ни одна `040-*` story не переводится в `2.todo`.

## Common Constraints
- Native Windows является supported surface, WSL остается отдельным environment.
- Default path работает least-privilege; elevation может быть только explicit.
- Git не должен случайно добавлять ChangeRail source через wiring targets.
- Bootstrap/verify/drift используют одну и ту же wiring classification.
- Command construction безопасно обрабатывает spaces и non-ASCII paths.
- Live-host evidence sanitized; credentials и host identities ignored.

## Provisional Series Cards
1. `040-01-add-windows-runtime-entrypoints.md`
2. `040-02-add-windows-wiring-backend.md`
3. `040-03-add-windows-verification-and-git-safety.md`
4. `040-04-add-windows-automated-smoke.md`
5. `040-05-prove-native-windows-end-to-end.md`

## Exit Gate
- Bootstrap и verify проходят на обоих Windows hosts из clean disposable clone.
- Skill/command discovery подтвержден на supported Windows agent surfaces.
- Git safety и drift checks подтверждены до и после ChangeRail update.
- Full release baseline остается green на primary Linux environment.
- Compatibility и migration docs отражают реальную support matrix.

## Related
- `openspec/board/1.backlog/030-00-native-windows-discovery-epic.md`
- `docs/compatibility.md`
- `docs/migration-guide.md`

## Result
not started

## Next
- Не выполнять до завершения и review `030-03`.

## Log
- 2026-08-01T15:07:29Z provisional epic создана отдельно от discovery series.
