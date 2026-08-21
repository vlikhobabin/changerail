# Возобновление retained payload после внешнего blocker

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
- Field validation supervised delivery, остановленной mandatory external
  platform verification gate.

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `yes`
- Credential or mutation authority: `yes`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

Published investigation `investigate-bounded-field-validation-batch` закрывает
repeated-defect classification для одного bounded external-blocker resume
hypothesis. Перед реализацией все еще требуется отдельная exact published
authorization card: change расширяет dirty retained-payload launch authority и
blocker/evidence wire contract.

## Depends On
- `support-runner-resume-after-investigation-required`
- `investigate-bounded-field-validation-batch`
- separate exact published authorization source for
  `resume-retained-payload-after-external-blocker`
- `enforce-declared-execution-target-invariant`

## Summary
Single-card и package resume сейчас разрешают exact dirty retained payload
только когда prior terminal reason равен `investigation_required`. Delivery
worker также может корректно остановиться после materializing implementation,
если mandatory external platform, service или credential gate временно
недоступен. Payload сохраняется, но runner не предлагает machine-checkable
resume path после восстановления external condition.

## Acceptance
- Runner моделирует recoverable external blockers через bounded structured
  contract вместо project-specific free-text terminal reasons.
- Blocked child сохраняет workspace/card/HEAD/tree/diff fingerprints без
  заявления successful delivery или bypass review.
- Если проект объявляет execution target, blocked child также сохраняет его
  logical id/fingerprint; blocker и resume evidence не разрешают provision,
  rebind или target substitution.
- Resume принимает dirty workspace только после валидации prior status, blocker
  class, exact retained fingerprint и declared resume evidence.
- Payload drift, другая card/workspace, missing evidence или unrecognized
  blocker fail closed до Codex launch.
- Target drift или другой target fingerprint fail closed. Явный target rebind
  требует нового clean delivery attempt и не может использовать dirty resume.
- `resume-plan` возобновляет original child и продолжает dependency queue;
  already delivered cards остаются skipped.
- Tests покрывают successful recovery, stale evidence, payload drift, mixed
  workspaces, nonrecoverable blockers и compatibility existing investigation
  authorization path.

## Change Set
- `resume-retained-payload-after-external-blocker`

## Verify
- `python3 scripts/smoke-contract-schemas.py`
- `python3 scripts/smoke-delivery-runner.py`
- `bin/openspec validate --all --strict`
- `python3 scripts/public-surface-scan.py`

## Archive
- not started

## Related
- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `scripts/smoke-delivery-runner.py`
- `openspec/board/4.done/support-runner-resume-after-investigation-required.md`
- `openspec/board/1.backlog/enforce-declared-execution-target-invariant.md`
- `openspec/changes/resume-retained-payload-after-external-blocker/`

## Result
Проработка завершена; apply-ready artifacts созданы, реализация не начата.

## Next
- После published investigation authorization выполнить
  `$chrl-deliver openspec/board/2.todo/resume-retained-payload-after-external-blocker.md`.

## Change 1: `resume-retained-payload-after-external-blocker`

### Why
Корректно сохраненный payload после временно недоступной обязательной внешней
проверки нельзя продолжить поддерживаемым machine-checkable путем.

### Goal
Добавить bounded external-blocker taxonomy, evidence-index policy и exact
fingerprint resume для single-card/queue без общего dirty-tree bypass.

### Scope
- authoritative blocker stop и retained identity;
- evidence-bound single-card resume;
- original-child `resume-plan` parity;
- schemas, stable failure reasons, adversarial fixtures and docs.

### Acceptance
- Только известный structured blocker с exact retained fingerprint и fresh
  scoped evidence разрешает resume.
- Wrong card/workspace, stale/missing evidence, drift и unknown class fail
  closed до Codex launch.
- Resumed lifecycle повторяет mandatory external gate и review/publish gates.
- Existing remote и `investigation_required` paths сохраняются.
- Для проекта с declared execution target retained/resume identity включает
  exact target id/fingerprint; external recovery не разрешает создание или
  подмену среды.

### Depends On
- `openspec/board/4.done/support-runner-resume-after-investigation-required.md`
- `investigate-bounded-field-validation-batch`
- separate exact published investigation authorization for this card's
  dirty-resume authority and blocker/evidence wire contract
- `openspec/board/2.todo/enforce-declared-execution-target-invariant.md`

### Related
- `openspec/changes/resume-retained-payload-after-external-blocker/`
- `openspec/board/4.done/investigate-bounded-field-validation-batch.md`

## Log
- 2026-08-20T07:55:00Z карточка создана из sanitized package-runner recovery
  finding.
- 2026-08-20T17:30:00Z той же delivery program потребовались три manual recovery
  sessions. Они сохранили useful JSONL evidence, но не имели delivery-run
  status, parent attempt id, structured blocker transition или aggregate
  token/timing record. Recovery lineage/status parity повышены в priority;
  retained-payload authorization model не меняется.
- 2026-08-21T07:43:31Z исследование выбрало value-free blocker object, scoped
  evidence-index freshness checks и exact fingerprint reuse; один OpenSpec
  change доведен до apply-ready artifacts.
- 2026-08-21: добавлен declared-target invariant: восстановление внешнего
  условия не разрешает provision/rebind/substitution, а target drift требует
  нового clean delivery attempt.
- 2026-08-21T09:10:00Z bounded field-validation investigation зафиксировало
  exact retained-payload resume hypothesis, ceiling 500, scoped evidence-index
  boundary и requirement нового split при повторе того же blocker.
