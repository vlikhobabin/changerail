## Context

ChangeRail уже хранит review-cycle history и запрещает publish без fresh
independent `GO`. Текущий documented rescue loop допускает два same-card
rescue-подхода после первого `NO-GO`, а следующий `NO-GO` становится safety
stop-ом. Это безопасно для supervised режима, но плохо подходит для автономного
aggregate delivery: root-orchestrator останавливается и ждет ручную
exceptional-authorization, хотя корректный следующий шаг часто можно выбрать
детерминированно.

Новая политика должна остаться generic core behavior для ChangeRail. Она не
должна зависеть от конкретного consumer workspace, приватных board conventions
или domain-specific extension.

## Goals / Non-Goals

**Goals:**
- Описать autonomous repeated `NO-GO` policy для unattended runs.
- Увеличить bounded same-card micro-rescue budget до пяти циклов, чтобы
  короткие исправления не создавали лишние карточки слишком рано.
- После исчерпания budget автоматически переводить работу в linked
  rescue/replacement карточку с полной историей prior cycles.
- Добавить lineage guard, который переводит повторяющийся класс blocker-а в
  investigation/design карточку вместо бесконечной цепочки implementation
  rescue-карточек.
- Сохранить invariant: `NO-GO` payload не публикуется без fresh independent
  `GO`.

**Non-Goals:**
- Не менять review verdict schema и terminal outcome enum.
- Не реализовывать генератор карточек в `bin/changerail-delivery-runner` в этом
  change. Runner остается fail-fast supervisor boundary, а card creation
  остается обязанностью lifecycle agent/skill.
- Не вводить workspace-specific названия, приватные пути или consumer-only
  policy.

## Decisions

1. **Пять same-card rescue cycles как автономный default.**
   Два цикла оказались слишком консервативны для unattended root delivery, где
   operator отсутствует по определению. Пять циклов дают агенту достаточно
   места для bounded micro-fixes, но сохраняют конечный лимит.

2. **Safety stop становится escalation boundary, а не ручным ожиданием.**
   После исчерпания same-card budget агент не просит exceptional authorization.
   Он фиксирует terminal `NO-GO`, оставляет dirty payload unpublished, создает
   linked rescue/replacement карточку и ставит ее следующей перед blocked
   downstream work.

3. **Новая карточка обязана переносить историю.**
   Replacement/rescue карточка должна включать source card, последнюю safe
   published reference, все prior `NO-GO` findings, сделанные rescue-попытки,
   retained evidence paths или их summaries, текущую гипотезу и explicit
   verification floor. Это превращает "сброс счетчика" в смену контекста с
   полной памятью, а не в обход gate.

4. **Lineage guard ограничивает цепочки карточек.**
   Если два linked replacement/rescue card подряд возвращают тот же blocker
   class или тот же unresolved invariant, следующая автономная карточка должна
   быть investigation/design, а не implementation. Investigation может вернуть
   implementation cards, `BLOCKED`, `SUPERSEDED` или `NOT-VERIFIABLE`.

5. **Runner остается fail-fast.**
   `run-plan`/`resume-plan` по-прежнему не запускает downstream cards после
   child `NO-GO`. Автономное recovery выполняется через новую linked карточку,
   после чего aggregate plan можно resume от published `GO` state.

## Risks / Trade-offs

- [Risk] Пять micro-rescue cycles могут тратить время на локальные фиксы.
  → Mitigation: конечный budget, replacement handoff и lineage guard.
- [Risk] Replacement card может стать формальным сбросом счетчика.
  → Mitigation: обязательная история prior cycles и escalation to investigation
  при повторении blocker class.
- [Risk] Автономная политика может создать карточку при внешнем blocker-е.
  → Mitigation: external dependency cases остаются `BLOCKED` с concrete
  evidence: credentials, network, license, missing stand или unavailable tool.
- [Risk] Investigation может показать, что feature больше непроверяема или не
  нужна.
  → Mitigation: documented outcomes `NOT-VERIFIABLE` или `SUPERSEDED` допустимы
  как terminal planning decisions и не требуют publish negative-reviewed code.
