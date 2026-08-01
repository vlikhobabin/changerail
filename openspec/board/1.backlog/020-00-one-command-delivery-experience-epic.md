# Серия 020: Надежный one-command delivery

## Status
1.backlog

## Owner
ChangeRail core

## OpenSpec Stage
epic

## Series
`020-one-command-delivery-experience`

## Series Index
`00`

## Delivery Mode
coordination-only; не запускать `$chrl-deliver` для этой epic-карточки

## Source
- Два consumer delivery run завершились публикацией, но потребовали ручной
  orchestration и восстановления контекста из runtime logs.

## Summary
Сделать путь `accepted card -> $chrl-deliver <card> -> reviewed publish`
предсказуемым для оператора: определить readiness, удерживать evidence,
диагностировать и возобновлять remote preflight, явно считать review rescue
budget и доказать полный flow интеграционным smoke.

## Series Goal
Обычный operator workflow использует одну команду и structured runtime state;
phase-команды остаются repair/debug/manual-resume surface. Transient stop не
требует ручной реконструкции контекста, а safety gates остаются fail-closed.

## Entry Gate
- Серия `010-core-release-contracts` завершена: карточки `010-01`..`010-05`
  опубликованы и находятся в `4.done`.
- Post-push release baseline после `010-05` прошел 26/26 на
  `2026-08-01T21:24:05Z` readiness pass.
- Все карточки этой серии повторно актуализированы против итоговых runtime,
  manifest, publish и verification contracts.

## Common Constraints
- Не ослаблять independent review, scope или publish target proof.
- Не делать infinite retry/review loops.
- Raw logs и mutable state остаются ignored.
- Phase commands сохраняют backward-compatible manual recovery value.
- Нормальный путь в docs начинается с `$chrl-deliver`, а не с ручной цепочки.

## Implementation Recommendations
- Сначала определить card readiness без добавления новой board lane.
- Затем создать общий retained evidence mechanism.
- Remote resume должен потреблять structured evidence и всегда повторять fresh
  preflight перед продолжением.
- Rescue counters строить после стабилизации run/evidence contracts.
- Закрыть серию end-to-end fixture с local bare remote и controlled failures.

## Series Cards
1. `020-01-formalize-deliver-ready-card-contract.md`
2. `020-02-add-retained-delivery-evidence.md`
3. `020-03-add-remote-preflight-diagnostics-and-resume.md`
4. `020-04-model-review-rescue-budget.md`
5. `020-05-prove-one-command-delivery-regression.md`

## Exit Gate
- Все series cards опубликованы или явно заменены.
- One-command regression проходит success, transient resume и no-go paths.
- Docs, skills, runner status, metrics и schemas используют одинаковые terms.
- Серия `030` повторно сверена с итоговым cross-platform runtime surface.

## Related
- `openspec/board/1.backlog/010-00-core-release-contracts-epic.md`
- `openspec/board/1.backlog/030-00-native-windows-discovery-epic.md`
- `skills/changerail-deliver/SKILL.md`
- `bin/changerail-delivery-runner`

## Result
ready for tracked runner plan

## Next
- Создать и проверить tracked runner plan `020-one-command-delivery-experience`.

## Log
- 2026-08-01T15:07:29Z epic создана из объединенного consumer delivery feedback.
- 2026-08-01T21:24:05Z readiness pass после exit audit серии `010`: серия
  остается единой, story cards `020-01`..`020-05` готовятся к `2.todo` и
  package runner plan.
