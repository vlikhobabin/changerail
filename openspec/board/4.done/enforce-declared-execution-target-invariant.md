# Запретить неявную подмену объявленной среды выполнения

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

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
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `{"authorization_card":"openspec/board/4.done/authorize-bounded-execution-target-payload.md","authorization_id":"authorize-bounded-execution-target-payload"}`

Published investigation `investigate-bounded-field-validation-batch` закрывает
repeated-defect classification для одного bounded target-identity hypothesis.
Exact authorization source `authorize-bounded-execution-target-payload`
публикует bounded source для нового project/delivery/evidence contract и
обязательного fail-closed preflight.

## Depends On
- `investigate-bounded-field-validation-batch`
- `authorize-bounded-execution-target-payload`

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
- Shared declaration validator удерживает exact payload не выше 500 added
  production-counted LOC; более крупный payload требует split до review.
- Public surface не содержит названий частных проектов, платформенных правил,
  реальных адресов, учетных данных или runtime evidence.

## Change Set
- `enforce-declared-execution-target-invariant`

## Verify
- `python3 scripts/smoke-contract-schemas.py`
- `python3 scripts/smoke-verify-project.py`
- `python3 scripts/smoke-delivery-manifest.py`
- `python3 scripts/smoke-retained-evidence.py`
- `python3 scripts/smoke-delivery-runner.py`
- `python3 scripts/smoke-review-preflight.py`
- `bin/openspec validate --all --strict`
- `git diff --check`
- `python3 scripts/public-surface-scan.py`

## Archive
- `openspec/changes/archive/2026-08-21-enforce-declared-execution-target-invariant/`

## Related
- `AGENTS.shared.md`
- `skills/changerail-ff/SKILL.md`
- `skills/changerail-do/SKILL.md`
- `skills/changerail-review/SKILL.md`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `openspec/board/2.todo/define-verification-coverage-map.md`
- `openspec/board/2.todo/resume-retained-payload-after-external-blocker.md`
- `openspec/board/4.done/authorize-bounded-execution-target-payload.md`
- `openspec/changes/archive/2026-08-21-enforce-declared-execution-target-invariant/`

## Result
Реализация завершена: добавлены optional execution-target contract, shared
loader/projection, fail-closed manifest/verification/runner/evidence/review
gates, lifecycle guidance, template example и synthetic smoke coverage.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `enforce-declared-execution-target-invariant`

### Why
Delivery evidence может быть green на substitute target, если project-specific
oracle не переносит identity через общий ChangeRail lifecycle.

### Goal
Добавить optional tracked target identity, exact evidence/recovery binding и
fail-closed substitution policy без platform-specific provision logic.

### Scope
- `changerail.execution-target.v1` declaration и schema projections;
- shared loader для manifest, verification, runner и review preflight;
- target-bound evidence, blocker/resume и clean rebind semantics;
- lifecycle skills, templates, docs и synthetic fixtures.

### Acceptance
- Проекты с declaration проходят lifecycle только с exact matching target
  identity; legacy projects без declaration сохраняют текущий flow.
- Endpoint, credentials и target contents не попадают в tracked/status data.
- Missing/multiple/mismatched identity и substitution fail closed до
  review/publish или retained child launch.
- Added production-counted LOC не превышает 500 и использует один shared
  loader/comparator.

### Depends On
- `investigate-bounded-field-validation-batch`
- separate exact published investigation authorization for this card's target
  identity protocol

### Related
- `openspec/changes/enforce-declared-execution-target-invariant/`
- `openspec/board/4.done/investigate-bounded-field-validation-batch.md`

## Log
- 2026-08-21 карточка создана по подтвержденному случаю неявной подмены среды
  выполнения после отказа штатного маршрута.
- 2026-08-21T08:38:00Z `$changerail-ff` выбрал один optional tracked contract,
  shared validator и bounded implementation ceiling 500; apply-ready proposal,
  design, delta specs и tasks созданы.
- 2026-08-21T09:10:00Z bounded field-validation investigation зафиксировало
  exact target-identity hypothesis, ceiling 500, shared loader/comparator
  boundary и requirement нового split при повторе того же blocker.
- 2026-08-21T09:10:47Z linked exact published authorization source
  `authorize-bounded-execution-target-payload`; successor remains queued until
  that source is published in `4.done`.
- 2026-08-21T13:10:00Z implementation completed; focused contract,
  verify-project, manifest, evidence, runner and review-preflight smokes passed
  before OpenSpec sync/archive.
- 2026-08-21T13:15:00Z OpenSpec change archived as
  `openspec/changes/archive/2026-08-21-enforce-declared-execution-target-invariant/`.
- 2026-08-21T13:30:00Z independent review returned NO-GO for missing
  single-card post-child target drift gate and shortened public-safety
  redaction wording; scoped fixes added and runner/verify-project gates rerun.
- 2026-08-21T14:00:00Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
