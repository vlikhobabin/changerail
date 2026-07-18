## Context

`changerail-do` ограничивает локальный implement/verify loop параметром
`--max-fix-cycles` (default `2`), а `changerail-deliver` отдельно ограничивает
post-review rescue loop параметром `--max-review-cycles` (default `5`). Сейчас
первый safety stop не имеет явного перехода во второй orchestration layer:
агент может запросить ручное увеличение budget, остановиться без structured
handoff или ошибочно описать ситуацию как repeated review `NO-GO`.

Source of truth для поведения — canonical skills в `skills/`, shared rules в
`AGENTS.shared.md` и public methodology docs. `templates/project/AGENTS.md.tpl`
передает тот же contract новым consumer repositories; bootstrap smoke должен
защищать эту формулировку от drift.

## Goals / Non-Goals

**Goals:**

- Развести pre-review fix cycles и independent-review rescue cycles.
- Определить детерминированные ветви для bounded same-card micro-fix, отдельной
  recovery work и external/unavailable blocker.
- Сделать `fix_budget_exhausted` явным non-delivered handoff из
  `changerail-do` в supervising `changerail-deliver`.
- Передать одинаковые правила в consumer templates.

**Non-Goals:**

- Не менять default budgets `2` и `5`.
- Не разрешать бесконечный same-card loop.
- Не создавать implementation cards для внешней недоступности, отсутствующей
  authority или иных blockers, которые кодом не устраняются.
- Не менять wire schemas в этом change; это делает зависимый runner change.

## Decisions

1. **Fix budget и review budget остаются разными счетчиками.**
   `max-fix-cycles` ограничивает implement/verify attempts до independent
   review. `max-review-cycles` ограничивает same-card rescue/re-review attempts
   после review `NO-GO`. Исчерпание первого не расходует и не имитирует второй.

2. **`changerail-do` завершает safety stop строгим terminal handoff.**
   Финальный ответ содержит отдельные machine-readable строки
   `terminal_outcome: BLOCKED` и
   `terminal_reason: fix_budget_exhausted`. Runner будет читать их только из
   completed agent-message JSONL event, а не искать похожие слова в произвольном
   log text.

3. **Supervising deliver выбирает одну из трех ветвей.**
   Bounded micro-fix допустим в той же карточке, только если он локален,
   сохраняет declared capability/scope, не требует новой authority и имеет
   конкретную verification target. Отдельная capability, новый deliverable,
   расширение acceptance или самостоятельный риск получают linked
   rescue/replacement card. External blocker остается `BLOCKED` или
   `NOT-VERIFIABLE` с evidence и resume condition.

4. **Manual exceptional budget не является default recovery.**
   Оркестратор либо выполняет один bounded scoped continuation под собственным
   budget, либо материализует отдельную работу карточкой. Ручная authority
   запрашивается только тогда, когда действие само по себе выходит за
   разрешенный scope, а не из-за исчерпания внутреннего счетчика.

5. **Consumer guidance генерируется из tracked template.**
   `templates/project/AGENTS.md.tpl` получает краткий contract, а bootstrap
   smoke проверяет ключевые marker terms. Component-specific AGENTS могут
   уточнять safety boundaries, но не переопределяют общую семантику budgets.

## Risks / Trade-offs

- [Риск] Агент назовет крупный fix «micro-fix» и обойдет декомпозицию. →
  Ограничить ветвь observable criteria: тот же capability/scope, отсутствие
  новой authority и одна конкретная verification target.
- [Риск] Structured marker попадет в обычный prose. → Runner принимает marker
  только из completed agent-message event и только в exact line format.
- [Риск] Docs и templates разойдутся. → Добавить bootstrap/wiring smoke markers
  и проверять canonical skills вместе с public docs.

## Migration Plan

Обновить canonical skills, shared methodology, public docs и template; затем
прогнать skill, bootstrap и wiring smoke. Existing consumer repositories
получат новое правило при следующем bootstrap/migration sync; wire contracts и
старые runtime records остаются совместимыми.

## Open Questions

Нет. Machine enforcement и recovery-plan resume semantics определяются в
`enforce-fix-budget-terminal-and-recovery`.
