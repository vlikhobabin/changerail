# Публиковать структурированный live progress доставки

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
- Наблюдение supervised package delivery с long-running single-card child.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `yes`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

Перед implementation review требуется exact published investigation
authorization для нового progress event/status wire contract.

## Summary
Пока Codex child работает, single-card status показывает только
`phase=delivery`, `result=RUNNING`, process id и исходное start time. Aggregate
plan mirror только `state=running`. Оператор не может различить active
discovery, planning, implementation, verification или review без чтения raw
JSONL, который может содержать credentials/private runtime data и намеренно не
является supported status surface.

Добавить bounded secret-safe progress protocol, чтобы orchestrator наблюдал
долгую delivery без scraping child prose, commands, stdout или stderr.

## Acceptance
- Running single-card status содержит schema-versioned объект `progress` с
  bounded phase/stage enum, heartbeat timestamp и monotonic event counter.
- Child или runner обновляет progress с documented interval и на major
  transitions `ff -> do -> review -> publish` без parsing free-form prose.
- Aggregate plan status mirror latest safe child progress и timestamp.
- Progress не содержит prompts, shell commands, paths вне normalized
  card/workspace identifiers, environment values, response bodies или raw log
  excerpts.
- Stalled-child diagnostic использует heartbeat age и process state, но не
  завершает и не классифицирует live child только из-за одного missed interval.
- Tests покрывают normal progress, stale heartbeat, child termination, resume
  и redaction/non-disclosure invariants.
- Existing terminal status, raw evidence retention и single-card/package
  compatibility не меняются.

## Change Set
- `expose-structured-live-delivery-progress`

## Verify
- Contract/schema tests для single-card и aggregate status records.
- Runner integration fixture с deterministic progress events и stalled
  heartbeat.
- Secret-bearing synthetic child output доказывает value-free progress.

## Archive
- not started

## Related
- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `openspec/changes/expose-structured-live-delivery-progress/`

## Result
Проработка завершена; apply-ready artifacts созданы, реализация не начата.

## Next
- После published investigation authorization выполнить
  `$chrl-deliver openspec/board/2.todo/expose-structured-live-delivery-progress.md`.

## Change 1: `expose-structured-live-delivery-progress`

### Why
Поддерживаемый status не отличает активный lifecycle от зависшего child, а raw
JSONL не является безопасной operator surface.

### Goal
Добавить runner-owned bounded progress/heartbeat contract, explicit lifecycle
events, aggregate mirror и non-terminal stale diagnostics без разбора prose,
commands или output values.

### Scope
- delivery-run и plan-status schemas;
- runner event transport, heartbeat и status views;
- canonical lifecycle skills/wrappers;
- focused contract/runner smokes и operator docs.

### Acceptance
- Single-card и aggregate status показывают schema-valid phase/stage,
  heartbeat, monotonic counter и bounded health.
- Secret-bearing/free-form child data не может изменить или попасть в progress.
- Один stale interval не завершает и не переклассифицирует живой child.
- Existing terminal/raw-evidence/package compatibility сохраняется.

### Depends On
- exact published investigation authorization for this card's progress
  event/status wire contract

### Related
- `openspec/changes/expose-structured-live-delivery-progress/`

## Log
- 2026-08-20T09:54:00Z карточка создана из sanitized supervised delivery
  evidence.
- 2026-08-20T17:30:00Z следующая single-card delivery выполнялась 103 минуты и
  выдала 455 command executions, но public status оставался на coarse delivery
  phase. Orchestrator не мог различить source authoring, platform build, runtime
  proof, review wait, rescue или publish. Priority повышен перед следующим
  multi-card package run.
- 2026-08-21T07:43:31Z исследование выбрало runner-owned value-free event
  channel, coalesced activity heartbeat и non-terminal stale diagnostic; один
  OpenSpec change доведен до apply-ready artifacts.
