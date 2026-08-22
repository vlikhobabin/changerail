# Исследовать границу авторизации phase-routed delivery

## Status
2.todo

## Owner
ChangeRail maintainers

## OpenSpec Stage
story

## Series
- none

## Series Index
- none

## Source
- Независимый review cycle 3 карточки
  `add-phase-routed-delivery-plan-execution` завершился `NO-GO`: пять blocker
  findings и один major finding.
- Локальный review fingerprint:
  `sha256:93b354321da8e60e85508c622c96f6c477e2f5fba383efd30dc684b002694cbe`.

## Summary
Опубликовать decision-only investigation для новой границы авторизации между
aggregate phase runner и single-card child preflight. Исследование должно
выбрать один непротиворечивый wire contract для budget, card identity,
blocked-phase resume и aggregate runtime root, а затем назвать точную
replacement-карточку и ее обязательную regression matrix.

Текущий payload основной карточки является входом исследования, но не
разрешенной к публикации реализацией. Бюджет same-card rescue исчерпан; эта
карточка не разрешает третий repair и не запускает продуктовый pilot wave.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `yes`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

Исследование только фиксирует решение. Оно не изменяет production runner,
schemas или действующие authorization semantics.

## Blocks
- Публикацию `add-phase-routed-delivery-plan-execution`.
- Создание и выполнение точной replacement/rescue-карточки.
- Двухкарточный pilot wave phase-routed batch runner.

## Decision Questions
- Должен ли `max_repair_cycles` стать обязательным полем phase-routed plan или
  иметь единый schema/aggregate/child default; какое значение является
  каноническим.
- Какая комбинация полей однозначно идентифицирует plan card при допустимом
  отличии declared card id от filename stem.
- Как `resume-plan` создает канонический parent status для нового aggregate и
  child run до dirty-worktree preflight, сохраняя lineage с предыдущей
  попыткой.
- Какой exact transition разрешает повтор той же фазы после реального
  `BLOCKED` receipt и какие terminal receipts остаются не возобновляемыми.
- Поддерживает ли phase-routed mode нестандартный aggregate `--runtime-root`.
  Если да, как он входит в валидируемый parent/child contract; если нет, где
  admission обязан отклонить его до запуска child.
- Какие поля parent status являются provenance, какие являются authority, и
  какие same-user tampering scenarios должны завершаться fail closed.
- Можно ли уложить replacement payload в bounded production LOC ceiling без
  ослабления проверок или его необходимо разделить на несколько ordered cards.

## Acceptance
- Для каждого decision question выбран ровно один вариант, описаны причины и
  отвергнутые альтернативы.
- Зафиксирован единый contract для отсутствующего `max_repair_cycles`, который
  одинаково применяется schema validation, aggregate transition и child
  authorization.
- Зафиксирована canonical card identity, поддерживающая schema-valid alias id
  без неоднозначного поиска по card path/workspace.
- Зафиксирован resume protocol: новый aggregate/child identity существует в
  schema-valid canonical parent status до child preflight, previous run
  сохраняется как lineage, а exact `BLOCKED` transition не открывает reusable
  dirty-tree bypass.
- Для alternate aggregate runtime root принято бинарное решение: полная
  contract binding и verification либо ранний admission reject. Публичный CLI
  и docs не должны обещать неподдерживаемый вариант.
- Описана новая authority/wire boundary и минимальный набор полей, достаточный
  для fail-closed проверки plan, aggregate run, workspace, card, phase,
  attempt, child run/status path и payload fingerprint.
- Названы точные successor id и board path. Продолжение оформляется новой
  linked replacement-карточкой, а не третьим repair исходной карточки.
- Указана необходимость отдельной published authorization-карточки, которая
  связывает это investigation с exact successor и устанавливает
  `allow_new_authority_or_wire_protocol: true` и bounded production LOC
  ceiling.
- Verification floor successor включает production aggregate-to-child probes
  для explicit и omitted repair budget, aliased card id, реального `BLOCKED`
  receipt, нового resume run id, выбранной политики alternate runtime root и
  same-user tampering negative cases.
- Aggregate/resume smoke использует production single-card preflight на
  authorization boundary; fake child остается допустим только для тестов,
  которые не заявляют проверку этой границы.
- Исследование не изменяет production code, schemas и runtime behavior.

## Non-Goals
- Исправлять `bin/changerail-delivery-runner` в этой карточке.
- Публиковать текущий `NO-GO` payload основной карточки.
- Делать третий same-card repair или сбрасывать review history.
- Создавать broad authorization, применимый к произвольным будущим runner
  protocols.
- Запускать pilot wave до fresh independent `GO` successor-карточки.

## Change Set
- none yet

## Verify
- `bin/openspec validate --all --strict`
- `python3 scripts/public-surface-scan.py`
- `git diff --check`
- `bin/changerail-delivery-manifest scope-check <manifest> --workspace . --target working-tree --json`

## Archive
- not started

## Related
- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-plan.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `schemas/changerail-delivery-run.schema.json`
- `scripts/smoke-delivery-runner.py`
- `docs/changerail-contracts.md`

## Result
not started

## Next
- Выполнить `$chrl-deliver` для публикации decision-only investigation.
- По опубликованному решению создать exact replacement и отдельную bounded
  authorization-карточку.

## Change 1: `decide-phase-routed-delivery-authorization-boundary`

### Why
Два bounded repairs закрыли исходные дефекты, но независимый cycle-3 review
обнаружил противоречия между публичными schema/CLI promises и production child
authorization. Реализация вводит новую dirty-worktree authority/wire boundary,
для которой отсутствует опубликованное investigation authorization.

### Goal
Опубликовать одно ограниченное архитектурное решение, которое устраняет
неоднозначность phase-routed aggregate/child protocol и задает exact scope для
replacement implementation.

### Scope
- Воспроизвести и классифицировать cycle-3 R1-R6 по публичным контрактам.
- Выбрать canonical budget, card identity, resume и runtime-root semantics.
- Описать минимальную authority boundary и fail-closed invariants.
- Назвать exact replacement id/path и bounded verification floor.
- Не изменять production implementation в decision-only change.

### Acceptance
- Все вопросы из `Decision Questions` получают однозначное опубликованное
  решение.
- Решение связывает каждый cycle-3 blocker с contract choice и обязательным
  successor regression probe.
- Exact successor и отдельная authorization-карточка могут быть созданы без
  дополнительных продуктовых решений оператора.

### Depends On
- none

### Related
- `openspec/changes/decide-phase-routed-delivery-authorization-boundary/`

## Log
- 2026-08-22T13:12:37Z создана после fresh cycle-3 `NO-GO`; исходная карточка
  исчерпала две разрешенные same-card rescue attempts.
