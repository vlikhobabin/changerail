# Реализовать phase-routed delivery authorization boundary

## Status
2.todo

## Owner
unassigned

## OpenSpec Stage
not-started

## Series
- none

## Series Index
- none

## Source
- `investigate-phase-routed-delivery-authorization-boundary`
- Независимый review отклонённого payload
  `add-phase-routed-delivery-plan-execution`; same-card repair budget исчерпан.

## Summary
Заменить отклонённый phase-routed payload одной bounded реализацией выбранного
aggregate-to-child authorization contract. Runner должен fail closed связывать
plan, workspace, canonical card path, aggregate/child run identity, phase,
attempt, payload fingerprint и разрешённый `BLOCKED` resume transition.

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `yes`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `{"authorization_card":"openspec/board/4.done/authorize-bounded-phase-routed-delivery-payload.md","authorization_id":"authorize-bounded-phase-routed-delivery-payload"}`

## Depends On
- `investigate-phase-routed-delivery-authorization-boundary`
- `authorize-bounded-phase-routed-delivery-payload`

## Blocks
- Двухкарточный pilot wave phase-routed batch runner.

## Acceptance
- Phase-routed plan schema требует explicit `max_repair_cycles`; omitted value
  отклоняется до aggregate/child launch, а monolithic contract не меняется.
- Plan card разрешается по unique workspace identity и canonical card path;
  declared alias id сохраняется как wire identity без filename-stem lookup.
- Новый aggregate/child run получает schema-valid canonical parent status до
  production child preflight и сохраняет previous-run status fingerprint как
  lineage, не authority.
- Resume допускает только same-phase real `BLOCKED`, увеличивает attempt ровно
  на один и сохраняет payload; terminal, malformed, drifted и exhausted states
  невозобновляемы.
- Alternate aggregate `--runtime-root` отклоняется на phase-routed admission до
  child launch; monolithic behavior сохраняется.
- Parent status связывает plan, aggregate run, workspace, card, phase, attempt,
  child run/status path, payload fingerprint и transition-specific fields;
  несогласованный same-user tampering завершается fail closed.
- Added production-counted LOC не превышает 500; превышение требует нового
  investigation, а не split без отдельного решения или ослабления проверок.
- Production aggregate-to-child regression probes покрывают explicit и omitted
  repair budget, aliased card id, real `BLOCKED` receipt, новый resume run id,
  alternate runtime root rejection и same-user tampering negatives.
- Проверка authorization boundary использует production single-card preflight;
  fake child не является evidence для этой границы.
- Все deterministic checks проходят, затем fresh Sol review возвращает `GO`.

## Non-Goals
- Возобновлять или публиковать отклонённую исходную карточку.
- Разрешать arbitrary runtime roots или reusable dirty-tree bypass.
- Добавлять cryptographic trust или защищаться от полной согласованной подмены
  всех same-user local artifacts.
- Запускать pilot wave до публикации этой карточки с fresh independent `GO`.

## Change Set
- `implement-phase-routed-delivery-authorization-boundary`

## Verify
- `python3 scripts/smoke-delivery-runner.py`
- `python3 scripts/smoke-contract-schemas.py`
- `python3 scripts/smoke-review-preflight.py`
- `bin/openspec validate --all --strict`
- `python3 scripts/run-release-baseline.py`
- `python3 scripts/public-surface-scan.py`
- `git diff --check`

## Archive
- pending

## Related
- `openspec/board/4.done/investigate-phase-routed-delivery-authorization-boundary.md`
- `openspec/board/4.done/authorize-bounded-phase-routed-delivery-payload.md`
- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-plan.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `schemas/changerail-delivery-run.schema.json`
- `scripts/smoke-delivery-runner.py`
- `scripts/smoke-review-preflight.py`
- `openspec/specs/changerail-delivery-runner/spec.md`

## Result
pending

## Next
- Wait for published authorization, then run `$changerail-ff` for this card.

## Change 1: `implement-phase-routed-delivery-authorization-boundary`

### Why
Отклонённый payload не связывает budget, alias card identity, parent creation,
resume transition и runtime root достаточно строго для fail-closed child
authorization.

### Goal
Реализовать одну bounded production contract correction и regression matrix,
выбранные опубликованным investigation.

### Scope
- Обновить phase-routed plan/status schemas и aggregate admission/transition
  logic в пределах exact selected decisions.
- Использовать production single-card preflight для authorization-boundary
  probes и сохранить fake child только вне этих claims.
- Обновить canonical contracts/docs только для наблюдаемого нового behavior.

### Acceptance
- Все card-level acceptance criteria имеют deterministic positive/negative
  evidence.
- Scope соответствует exact authorization и укладывается в ceiling 500.
- Independent review проверяет implementation против investigation, source
  authorization и regression matrix.

### Depends On
- `authorize-bounded-phase-routed-delivery-payload`

### Related
- `openspec/changes/implement-phase-routed-delivery-authorization-boundary/`

## Log
- 2026-08-22T00:00:00Z created as the exact replacement selected by the
  published investigation; implementation remains blocked on authorization.
