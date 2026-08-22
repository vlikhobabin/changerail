# Исследовать границу авторизации phase-routed delivery

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
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

Исследование только фиксирует решение. Оно не изменяет production runner,
schemas или действующие authorization semantics.

## Blocks
- Публикацию `add-phase-routed-delivery-plan-execution`.
- Создание и выполнение exact replacement
  `openspec/board/2.todo/implement-phase-routed-delivery-authorization-boundary.md`.
- Публикацию exact authorization source
  `openspec/board/4.done/authorize-bounded-phase-routed-delivery-payload.md`.
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

## Selected Decisions
- `max_repair_cycles` обязателен для phase routing; отсутствие
  отклоняет plan до aggregate/child launch. Defaults 0 и 1 отвергнуты
  как неявный operator intent.
- Card lookup использует unique workspace identity и canonical resolved
  card path; declared plan id остается wire identity и может
  отличаться от filename stem.
- `resume-plan` до production child preflight атомарно пишет
  schema-valid canonical parent для нового aggregate/child run и
  связывает его с previous-run status fingerprint.
- Resume разрешает только `phase=P, attempt=N, BLOCKED ->
  phase=P, attempt=N+1`; terminal `DELIVERED`, review `GO`, exhausted-budget
  `NO-GO`, invalid receipt, plan drift и payload drift невозобновляемы.
- Phase-routed mode отклоняет alternate aggregate `--runtime-root` на
  admission; monolithic mode сохраняет existing behavior.
- Parent authority минимально связывает plan, aggregate run,
  workspace, card, phase, attempt, child run/status path, payload fingerprint и
  transition-specific repair/resume fields. Provenance не дает bypass;
  несогласованное same-user tampering fail closed, но полная
  согласованная подмена остается вне non-cryptographic trust model.
- Exact replacement — `implement-phase-routed-delivery-authorization-boundary`
  в
  `openspec/board/2.todo/implement-phase-routed-delivery-authorization-boundary.md`;
  exact separate authorization —
  `authorize-bounded-phase-routed-delivery-payload` с ceiling 500 и
  `allow_new_authority_or_wire_protocol: true`. Одна atomic replacement-карточка
  выбрана вместо split; превышение 500 требует нового
  investigation, а не ослабления tests.

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
- `decide-phase-routed-delivery-authorization-boundary`

## Verify
- PASS — `bin/openspec validate "decide-phase-routed-delivery-authorization-boundary" --strict`
- PASS — `bin/openspec validate "changerail-delivery-runner" --strict`
- PASS — `bin/openspec validate --all --strict` (24 passed, 0 failed)
- PASS — `python3 scripts/public-surface-scan.py` (0 findings)
- PASS — `git diff --check` и trailing-whitespace scan untracked artifacts
- PASS — `bin/changerail-delivery-manifest scope-check <manifest> --workspace . --target working-tree --json` (no missing, extra or mismatched paths)

## Archive
- `openspec/changes/archive/2026-08-22-decide-phase-routed-delivery-authorization-boundary/`

## Related
- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-plan.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `schemas/changerail-delivery-run.schema.json`
- `scripts/smoke-delivery-runner.py`
- `docs/changerail-contracts.md`
- `openspec/changes/archive/2026-08-22-decide-phase-routed-delivery-authorization-boundary/`

## Result
Decision-only investigation, spec sync и archive завершены. Production runner,
schemas, smoke implementation, CLI, public runtime docs и runtime behavior не
изменялись.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

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
- `openspec/changes/archive/2026-08-22-decide-phase-routed-delivery-authorization-boundary/`

## Log
- 2026-08-22T13:12:37Z создана после fresh cycle-3 `NO-GO`; исходная карточка
  исчерпала две разрешенные same-card rescue attempts.
- 2026-08-22T14:48:22Z `$changerail-ff` выбрал один
  aggregate/child authorization contract, создал apply-ready artifacts и
  подготовил decision-only handoff без production/runtime changes.
- 2026-08-22T14:53:21Z `$changerail-do` синхронизировал decision requirement,
  успешно выполнил strict/public-surface/scope проверки и архивировал change;
  карточка остается в `3.inprogress` для независимого review.
- 2026-08-22T14:54:13Z preflight классифицировал historic repeated defect class
  как payload risk; metadata уточнены: decision-only investigation является
  требуемым simplification и не содержит повторного implementation defect.
- 2026-08-22T15:36:03Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
