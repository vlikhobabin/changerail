# Перезапуск устаревших consumer agent sessions перед следующей работой

## Status
5.canceled

## Owner
operator

## OpenSpec Stage
not-applicable

## Source
- Follow-up from
  `openspec/board/4.done/finalize-known-consumer-migration-after-restart.md`.

## Summary
Карточка требовала остановить одну session family, запущенную до ChangeRail
wiring rollout, прежде чем снова использовать ее для consumer development.

## Cancellation Reason
- Исходная pre-rollout session family больше не существует в process state.
- Текущие long-lived sessions появились после rollout и не соответствуют
  acceptance scope этой карточки.
- Общая рекомендация начинать новую agent session на карточку уже находится в
  public workflow docs; machine-local process housekeeping принадлежит ignored
  operator inventory, а не product backlog.

## Verify
- Исходный process identifier из ignored migration inventory отсутствует.
- Public consumer names, paths и process ids не добавлены в эту карточку.

## Related
- `openspec/board/4.done/finalize-known-consumer-migration-after-restart.md`
- `docs/board-and-two-agent-feature-flow.md`

## Result
закрыто как no longer applicable; product implementation не требуется

## Next
- дальнейших действий нет

## Log
- 2026-07-12T09:20:17Z follow-up был создан после migration rollout.
- 2026-08-01T15:07:29Z исходный operational condition больше не существует;
  карточка закрыта как no longer applicable.
