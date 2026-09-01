# Повторно оценить phase-routed delivery после stable release

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

## Series
- none

## Series Index
- none

## Source
- Решение оператора от 2026-08-31 отложить phase-routed delivery и не включать
  отклоненную implementation lineage в первый stable release.

## Summary
Сохранить одну точку возврата к phase-routed multi-agent delivery без
продолжения старых authorization/rescue payloads. Новый triage должен заново
подтвердить пользовательскую ценность, bounded scope и более простой protocol
после выпуска стабильного core и сокращения общего долга.

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `yes`
- Credential or mutation authority: `no`
- Repeated defect class: `yes`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Entry Gate
- Первый stable release опубликован.
- Общий технический и операционный долг сокращен по отдельному принятому плану.
- Есть подтвержденный consumer use case, для которого monolithic delivery
  недостаточен.
- Новый investigation сравнивает упрощение/отказ от phase routing с новой
  реализацией и не переиспользует rejected forensic payload как authority.

## Acceptance
- До выполнения всех entry gates карточка не переводится в `2.todo`, не
  создает OpenSpec implementation changes, authorization или pilot wave.
- Новый triage учитывает опубликованные historical investigations, но заново
  выбирает scope, trust boundary, verification cost и rollout criteria.
- Любая будущая implementation lineage имеет новую source identity, bounded
  review budget и observable consumer outcome.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `openspec/board/5.canceled/implement-phase-routed-delivery-authorization-boundary.md`
- `openspec/board/4.done/investigate-phase-routed-delivery-authorization-boundary.md`
- `openspec/board/4.done/investigate-phase-routed-resume-integrity-rescue.md`
- `openspec/board/4.done/investigate-type-safe-decoded-target-classification-boundary.md`

## Result
deferred

## Next
- wait for all entry gates and an explicit operator triage decision

## Log
- 2026-08-31T00:00:00Z создана как единственная backlog-точка возврата;
  существующие rejected/local payloads не продолжаются.
