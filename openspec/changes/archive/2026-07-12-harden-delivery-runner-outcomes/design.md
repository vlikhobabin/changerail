## Context

`bin/changerail-delivery-runner` читает JSONL output от `codex exec` и
преобразует его в terminal supervisor outcome. Текущий parser рекурсивно искал
все строки во всех JSON objects и трактовал слова вроде `error`, `failed`,
`no-go` или `awaiting-review` как terminal outcome. Поэтому non-terminal tool
messages могли override actual delivery lifecycle. Отдельно `bin/verify-project`
проверял только три schemas, хотя ChangeRail уже публикует пять contract
schemas.

## Goals / Non-Goals

**Goals:**
- Считать terminal outcomes authoritative только из documented event types или
  explicit terminal fields.
- Сохранить ordered JSONL processing и позволить later terminal events
  supersede earlier non-terminal noise.
- Оставить process exit fallback: exit `0` означает `DELIVERED`, non-zero
  означает `BLOCKED`, если нет authoritative `NO-GO` или `BLOCKED` event.
- Гарантировать, что verification/release checks перечисляют все пять public
  schemas.

**Non-Goals:**
- Не менять delivery-run schema id.
- Не вводить batch semantics в single-card runner.
- Не добавлять remote CI infrastructure в этом change.

## Decisions

- Добавить event classifier, который смотрит только top-level event metadata:
  `type`, `event`, `name`, `terminal_outcome`, `terminal-outcome`, `outcome` и
  `result`, когда event сам является documented terminal event shape.
- Распознавать `external-review/no-go` как `NO-GO`, `awaiting-review` и
  `awaiting-external-review` как `BLOCKED`, а explicit terminal fields со
  значениями `delivered`, `no-go` или `blocked`.
- Обрабатывать stdout lines по порядку и возвращать последний authoritative
  terminal outcome. Это позволяет финальному lifecycle event supersede earlier
  status updates.
- Расширить schema filename tuple в `bin/verify-project` и обновить smoke
  expectations/docs, чтобы missing delivery-run или review-cycle-history schemas
  обнаруживались.

## Risks / Trade-offs

- [Risk] Старый producer output мог полагаться на loose arbitrary string
  matching. Mitigation: оставить только documented event names и explicit
  terminal fields; undocumented strings не должны быть supervisor contract.
- [Risk] Last-authoritative-wins может скрыть contradictory terminal events.
  Mitigation: focused tests покрывают conflict ordering; future metrics могут
  флагировать impossible event streams без изменения supervisor outcome сейчас.
- [Risk] Schema coverage дублируется в docs и helper constants. Mitigation:
  smoke tests assert, что helper покрывает complete public schema set.
