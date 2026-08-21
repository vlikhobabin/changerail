# Исследовать bounded границы следующего field-validation batch

## Status
2.todo

## Owner
ChangeRail maintainers

## OpenSpec Stage
artifacts

## Series
- none

## Series Index
- none

## Source
- Apply-ready artifacts шести связанных successor payloads.
- Deterministic review complexity contract: default 300 и bounded ceiling 500
  added production-counted LOC.
- Field evidence по coarse progress, external recovery, episode metrics,
  verification gaps, source classification drift и execution-target
  substitution.

## Summary
Перед implementation batch требуется public-safe investigation decision,
которая связывает каждый exact successor с узкой implementation boundary,
production LOC ceiling и verification floor. Decision также должна завершить
repeated-defect analysis для трех карточек: дальнейший successor является
bounded implementation выбранного решения, а не очередным неограниченным
rescue той же гипотезы.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Blocks
- `enforce-declared-execution-target-invariant`
- `expose-structured-live-delivery-progress`
- `resume-retained-payload-after-external-blocker`
- `report-recovery-aware-delivery-episodes`
- `define-verification-coverage-map`
- `materialize-versioned-source-classification-profiles`

## Acceptance
- Для каждого exact successor зафиксированы id, authorization-time path
  `3.inprogress`, accepted protocol boundary и ceiling не выше 500.
- Target invariant использует один shared declaration loader/comparator и не
  добавляет provider discovery/provision logic.
- Live progress использует bounded value-free event file/status projection и
  не парсит prose, commands или raw child output.
- External resume переиспользует existing retained identity/authorization
  helpers и ограничивает blocker taxonomy/evidence policy без общего dirty
  bypass.
- Episode/metrics payload переиспользует owner artifacts и делит production
  budget между runner lineage и metrics rollup без raw-log reconstruction.
- Verification coverage и source profile payloads используют по одному
  canonical loader/normalizer и не создают второй acceptance source of truth.
- Для target, external resume, verification coverage и source profiles
  investigation explicitly завершает repeated-defect classification; если
  bounded hypothesis снова не проходит, нужен новый linked investigation/split.
- Ни один decision не повышает global ceiling, не authorizes другой successor
  и не разрешает payload свыше 500 production-counted LOC.

## Investigation Decision
Каждый successor может получить отдельный clean tracked authorization source с
`production_loc_ceiling: 500` и
`allow_new_authority_or_wire_protocol: true`, только если сохраняет следующую
границу:

- `enforce-declared-execution-target-invariant`: один optional tracked
  declaration и shared loader/comparator; production wiring только manifest,
  `verify-project`, runner и review preflight.
- `expose-structured-live-delivery-progress`: один runner-owned bounded event
  transport, coalesced heartbeat и schema-valid aggregate projection; без
  child prose/log parsing и второго telemetry store.
- `resume-retained-payload-after-external-blocker`: existing retained
  fingerprint/authorization paths, closed blocker enum и scoped evidence index;
  без generic dirty-tree flag, credential handling или target rebind.
- `report-recovery-aware-delivery-episodes`: owner-generated episode/attempt
  ids и bounded derived rollup; runner lineage budget до 300 production LOC,
  metrics collection/output budget до 200, без raw-log reconstruction.
- `define-verification-coverage-map`: один five-field project map и derived
  runtime ledger, references to acceptance/tasks/evidence вместо их копий; один
  shared loader across planning, delivery, verification и review.
- `materialize-versioned-source-classification-profiles`: existing
  `.changerail/source-classification.yaml` остается единственным effective
  rules input; profile detection/materialization и drift report переиспользуют
  один canonical normalization path.

Для четырех карточек, созданных из repeated field defect, decision закрывает
неопределенную гипотезу и разрешает successor пометить
`Repeated defect class: no`: повторный symptom не дает дополнительного rescue
budget, а реализация ограничена exact decision выше. Превышение ceiling,
расширение protocol authority или повтор того же blocker требует нового split
или investigation, а не изменения authorization.

## Change Set
- `decide-bounded-field-validation-batch`

## Verify
- `bin/openspec validate decide-bounded-field-validation-batch --strict`
- `bin/openspec validate --all --strict`
- `python3 scripts/public-surface-scan.py`
- `git diff --check`

## Archive
- not started

## Related
- `openspec/changes/decide-bounded-field-validation-batch/`
- `scripts/changerail_review_preflight.py`
- `openspec/board/2.todo/enforce-declared-execution-target-invariant.md`
- `openspec/board/2.todo/expose-structured-live-delivery-progress.md`
- `openspec/board/2.todo/resume-retained-payload-after-external-blocker.md`
- `openspec/board/2.todo/report-recovery-aware-delivery-episodes.md`
- `openspec/board/2.todo/define-verification-coverage-map.md`
- `openspec/board/2.todo/materialize-versioned-source-classification-profiles.md`

## Result
Проработка завершена; apply-ready investigation artifacts созданы.

## Next
- Выполнить
  `$chrl-deliver openspec/board/2.todo/investigate-bounded-field-validation-batch.md`.

## Change 1: `decide-bounded-field-validation-batch`

### Why
Шесть protocol-bearing successors не могут пройти deterministic review без
published bounded decision; четыре также требуют завершить repeated-defect
analysis до implementation.

### Goal
Опубликовать per-successor boundaries, ceiling и verification floors для exact
authorization sources без production implementation.

### Scope
- exact successor ids и future `3.inprogress` paths;
- production path budgets и shared-helper constraints;
- repeated-defect simplification decisions;
- authorization and verification floor requirements.

### Acceptance
- Каждый successor имеет independent bounded decision не выше 500 LOC.
- Protocol allowance не распространяется на другой payload.
- Repeated-defect successor не получает новый rescue budget.
- Decision не меняет production code или global limits.

### Depends On
- none

### Related
- `openspec/changes/decide-bounded-field-validation-batch/`

## Log
- 2026-08-21T08:40:00Z создано общее investigation для шести exact payloads,
  необходимых перед package delivery исходных пяти карточек.
