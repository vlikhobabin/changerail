# Серия 010: Базовые release-контракты

## Status
4.done

## Owner
ChangeRail core

## OpenSpec Stage
epic

## Series
`010-core-release-contracts`

## Series Index
`00`

## Delivery Mode
coordination-only; не запускать `$chrl-deliver` для этой epic-карточки

## Source
- Triage consumer feedback и текущего ChangeRail backlog от 2026-08-01.

## Summary
Устранить дефекты, которые мешают считать текущий public surface надежной
основой для дальнейшего delivery и native Windows support: невалидные skill
metadata, неявный Python runtime, self-invalidating publish metadata,
непроверяемый manifest scope и негибкий consumer verifier.

## Series Goal
После серии основные skills загружаются детерминированно, runtime имеет
поддерживаемый bootstrap/diagnostic contract, publish ledger не пишет
невозможные данные в tracked card, manifest проверяет полный scope, а
`verify-project` различает обязательные и отключенные consumer surfaces.

## Common Constraints
- Сохранять fail-closed behavior для review, scope, publish и blocking checks.
- Не ослаблять проверки по умолчанию без явного project profile.
- Mutable runtime/publish state хранить только в ignored runtime artifacts.
- Не добавлять private consumer names, paths, credentials или raw logs.
- Для schema/CLI changes добавлять negative и migration coverage.

## Implementation Recommendations
- Сначала исправить skill discovery, чтобы последующие delivery-команды были
  доступны агентам.
- Затем зафиксировать единый Python runtime contract для всех helpers.
- Publish finalization и manifest scope менять последовательно: ledger model
  должен быть определен до handoff/scope enrichment.
- Verification profiles вводить последними, используя уже определенный runtime
  и не превращая legacy debt в неявный green result.

## Series Cards
1. `010-01-repair-skill-frontmatter-validation.md`
2. `010-02-establish-supported-python-runtime.md`
3. `010-03-fix-publish-finalization-ledger.md`
4. `010-04-add-manifest-scope-and-handoff.md`
5. `010-05-add-verification-profiles-and-severity.md`

## Exit Gate
- Все пять карточек опубликованы или явно закрыты с заменяющим решением.
- `python3 scripts/run-release-baseline.py` проходит.
- `python3 scripts/public-surface-scan.py --history` проходит.
- Серии `020` и `030` повторно актуализированы против итоговых contracts.

## Related
- `openspec/board/1.backlog/020-00-one-command-delivery-experience-epic.md`
- `openspec/board/1.backlog/030-00-native-windows-discovery-epic.md`
- `docs/release-discipline.md`
- `docs/changerail-contracts.md`

## Result
done; series `010` delivered and published

## Next
- Использовать завершенные contracts как entry gate для серий `020`-`040`.

## Log
- 2026-08-01T15:07:29Z epic создана при пересборке backlog.
- 2026-08-01T21:24:05Z все story cards `010-01`..`010-05` опубликованы,
  post-push release baseline прошел; серия закрыта как coordination epic.
