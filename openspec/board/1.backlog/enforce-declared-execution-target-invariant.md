# Запретить неявную подмену объявленной среды выполнения

## Status
1.backlog

## Owner
ChangeRail maintainers

## OpenSpec Stage
story

## Series
- none

## Series Index
- none

## Source
- Обезличенная полевая проверка: при временной недоступности штатного
  поставщика исполнитель создал другую среду выполнения и получил
  доказательства не на объявленной цели проекта.
- Связанные карточки verification coverage и external-blocker resume.

## Summary
ChangeRail не должен знать особенности конкретной платформы, базы данных или
поставщика, но обязан сохранять тождество среды, если проект объявил его частью
проверки. Сейчас карточка и evidence могут назвать команды, однако общий
delivery contract не запрещает агенту создать, клонировать, восстановить или
выбрать другую среду, чтобы обойти недоступность штатного маршрута.

Добавить универсальный договор объявленной цели выполнения. Проект владеет
логическим идентификатором, отпечатком и способом проверки; ChangeRail
переносит это тождество через planning, delivery, external blocker, resume и
independent review и запрещает неявную подмену.

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `yes`
- Credential or mutation authority: `no`
- Repeated defect class: `yes`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

Перед реализацией требуется exact published investigation authorization:
изменение добавляет новый project/delivery/evidence contract и обязательный
fail-closed preflight.

## Acceptance
- Проект может объявить универсальную цель выполнения: логический id,
  нечувствительный отпечаток и `target_substitution_policy: forbid`; физические
  адреса, учетные данные и содержимое среды в ChangeRail не передаются.
- `ff` и `do` сохраняют объявленную цель в tracked plan/manifest, а runtime
  evidence и terminal event ссылаются на тот же id/отпечаток без права агента
  изменить их через prompt или аргумент поставщика.
- Если acceptance требует одну среду, deterministic pre-review gate отклоняет
  отсутствие target evidence, другой отпечаток, несколько целей или
  доказательства, полученные после неявной подмены.
- Delivery skills явно запрещают создание, клонирование, восстановление,
  регистрацию или выбор другой среды как способ обойти недоступный provider,
  platform, service или credential gate.
- Недоступная или не совпавшая цель дает structured blocker до последующего
  действия, а не ручной запасной маршрут. Blocker и recovery evidence не дают
  authority на provision/rebind/substitution.
- Явное переподключение среды является отдельным операторским действием:
  меняет tracked target identity, начинает новую delivery attempt и делает
  прежние runtime evidence, review verdict и retained dirty-resume identity
  неприменимыми.
- Проекты без объявленной внешней цели сохраняют текущий generic workflow;
  ChangeRail не пытается обнаруживать или создавать среды самостоятельно.
- Synthetic fixtures покрывают совпадение, отсутствие цели, mismatch,
  несколько целей, попытку подмены при blocker/resume и явный новый запуск
  после rebind на абстрактных database/service примерах.
- Public surface не содержит названий частных проектов, платформенных правил,
  реальных адресов, учетных данных или runtime evidence.

## Change Set
- none yet

## Verify
- `python3 scripts/smoke-contract-schemas.py`
- `python3 scripts/smoke-delivery-runner.py`
- `python3 scripts/smoke-review-preflight.py`
- `bin/openspec validate --all --strict`
- `python3 scripts/public-surface-scan.py`

## Archive
- not started

## Related
- `AGENTS.shared.md`
- `skills/changerail-ff/SKILL.md`
- `skills/changerail-do/SKILL.md`
- `skills/changerail-review/SKILL.md`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `openspec/board/2.todo/define-verification-coverage-map.md`
- `openspec/board/2.todo/resume-retained-payload-after-external-blocker.md`

## Result
not started

## Next
- Получить published investigation authorization, затем выполнить
  `$changerail-ff` и определить минимальный generic contract без
  domain-specific логики.

## Log
- 2026-08-21 карточка создана по подтвержденному случаю неявной подмены среды
  выполнения после отказа штатного маршрута.
