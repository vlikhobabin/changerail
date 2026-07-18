## Why

Текущий `NO-GO` rescue loop защищает publish gate от бесконечного same-card
дожимания, но в автономном режиме он останавливает aggregate delivery и требует
ручной exceptional-authorization. Для unattended ChangeRail runs нужна
детерминированная политика, которая продолжает работу через явные карточки,
сохраняет review gate и не публикует negative-reviewed payload.

## What Changes

- Заменить ручную exceptional-authorization после repeated `NO-GO` на
  автономную escalation policy.
- Описать bounded same-card rescue budget, после которого агент создает linked
  rescue/replacement карточку с полной историей prior cycles.
- Добавить lineage guard: повторяющийся класс blocker-а между replacement
  карточками переводит работу в investigation/design карточку вместо очередной
  implementation rescue.
- Сохранить fail-closed publish invariant: payload после `NO-GO` никогда не
  публикуется без fresh independent `GO`.
- Обновить lifecycle skills, methodology docs, runner docs/specs и smoke drift
  checks под новую политику.

## Capabilities

### New Capabilities

### Modified Capabilities

- `changerail-agent-methodology`: автономная обработка repeated `NO-GO`,
  replacement/rescue карточки и investigation escalation.
- `changerail-skill-surface`: `changerail-deliver` и связанные lifecycle skills
  должны описывать автономный rescue budget вместо ручной exceptional
  authorization.
- `changerail-delivery-runner`: aggregate `run-plan`/`resume-plan` должен
  сохранять fail-fast semantics и документировать, что recovery выполняется
  новой linked карточкой, а downstream cards не запускаются до успешного
  published recovery.

## Impact

- `AGENTS.shared.md`, `docs/how-it-works.md`,
  `docs/board-and-two-agent-feature-flow.md`, `docs/changerail-contracts.md`.
- `skills/changerail-deliver/SKILL.md` и, при необходимости, runner-facing
  lifecycle text.
- `openspec/specs/*` delta specs для methodology, skill surface и delivery
  runner behavior.
- `scripts/smoke-wiring-discovery.py` regression strings, чтобы drift checks
  фиксировали новую autonomous policy.
- Breaking wire/API changes не ожидаются; изменение касается documented
  workflow semantics и agent instructions.
