# Публиковать структурированный live progress доставки

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
- Наблюдение supervised package delivery с long-running single-card child.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `yes`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `{"authorization_card":"openspec/board/4.done/authorize-bounded-live-progress-payload.md","authorization_id":"authorize-bounded-live-progress-payload"}`

Exact authorization source `authorize-bounded-live-progress-payload`
публикует bounded source для нового progress event/status wire contract.

## Depends On
- `investigate-bounded-field-validation-batch`
- `authorize-bounded-live-progress-payload`

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
- `python3 scripts/smoke-contract-schemas.py` - passed; delivery-run and
  plan-status progress/health fixtures validate and invalid enum/content
  fixtures fail closed.
- `python3 scripts/smoke-delivery-runner.py` - passed; normal progress,
  stale heartbeat, resume, child termination, aggregate mirror and
  non-disclosure fixtures passed.
- `bin/openspec validate expose-structured-live-delivery-progress --strict` -
  passed.
- `bin/openspec validate --all --strict` - passed, 32 items.
- `git diff --check` - passed.
- `python3 scripts/public-surface-scan.py` - passed, 1206 files scanned, 0
  findings.

## Archive
- `openspec/changes/archive/2026-08-21-expose-structured-live-delivery-progress/`

## Related
- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `openspec/changes/archive/2026-08-21-expose-structured-live-delivery-progress/`

## Result
Реализация завершена; bounded live progress protocol, aggregate mirror,
operator status view, lifecycle instructions, docs, tests and synced specs are
ready for independent review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

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
- `investigate-bounded-field-validation-batch`
- separate exact published investigation authorization for this card's progress
  event/status wire contract

### Related
- `openspec/changes/archive/2026-08-21-expose-structured-live-delivery-progress/`
- `openspec/board/4.done/investigate-bounded-field-validation-batch.md`

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
- 2026-08-21T09:10:00Z bounded field-validation investigation зафиксировало
  exact progress event/status boundary, ceiling 500 и запрет raw child
  prose/output parsing.
- 2026-08-21T14:10:59Z `$chrl-ff` подтвердил apply-ready artifacts,
  `bin/openspec validate expose-structured-live-delivery-progress --strict`,
  `bin/openspec validate --all --strict` и `git diff --check` прошли; карточка
  переведена в `3.inprogress` для delivery.
- 2026-08-21T14:30:05Z `$chrl-do` реализовал bounded progress event/status
  protocol, synced specs and docs, выполнил `python3
  scripts/smoke-contract-schemas.py`, `python3 scripts/smoke-delivery-runner.py`,
  `bin/openspec validate --all --strict`, `git diff --check` и `python3
  scripts/public-surface-scan.py`; change archived to
  `openspec/changes/archive/2026-08-21-expose-structured-live-delivery-progress/`.
- 2026-08-21T14:49:09Z focused re-review returned `NO-GO` for aliased queue
  card progress identity; same-card rescue fixed mirror identity to use child
  run id plus launched card path, added aliased queue progress smoke, and reran
  `python3 scripts/smoke-delivery-runner.py`, `python3
  scripts/smoke-contract-schemas.py`, `bin/openspec validate --all --strict`,
  `git diff --check` and `python3 scripts/public-surface-scan.py` successfully.
- 2026-08-21T14:56:23Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
