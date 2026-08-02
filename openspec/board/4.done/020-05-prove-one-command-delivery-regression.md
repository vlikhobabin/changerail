# Доказать one-command delivery интеграционным regression smoke

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
`020-one-command-delivery-experience`

## Series Index
`05`

## Source
- Series completion gate для consumer run class, породившего серии `010` и
  `020`.

## Summary
Создать deterministic end-to-end fixture, который проводит deliver-ready card
через planning, delivery, review, scoped publish и final ledger, а также
проверяет transient preflight resume и bounded no-go behavior.

## Acceptance
- Success fixture использует temporary repo и local bare remote без внешней
  сети.
- Flow начинается с deliver-ready card и одного orchestration entrypoint.
- Final card, Git history, manifest, verdict, evidence и runner status
  согласованы.
- Fixture доказывает отсутствие stale tracked publish metadata и extra scope.
- Отдельный сценарий останавливается и возобновляется после transient preflight.
- Отдельный сценарий fail-closed при stale verdict или exhausted review budget.
- Smoke входит в release baseline с bounded runtime.

## Scope
- Integration fixtures и минимальные test-only fake agent/reviewer surfaces.
- Release inventory/docs для нового smoke.

## Non-Goals
- Live network или реальный consumer repository в CI.
- Native Windows acceptance: серия `040`.

## Depends On
- `020-01-formalize-deliver-ready-card-contract`
- `020-02-add-retained-delivery-evidence`
- `020-03-add-remote-preflight-diagnostics-and-resume`
- `020-04-model-review-rescue-budget`

## Implementation Notes
- Проверять observable files/status/schema results, а не transcript wording.
- Fixture не должна требовать Codex credentials или расходовать network tokens.

## Change Set
- `prove-one-command-delivery-regression` (archived)

## Change 1: `prove-one-command-delivery-regression`

### Why
The series needs a deterministic end-to-end guard that proves the accepted-card
to reviewed-publish path and the transient/no-go failure paths without live
network or real consumer repositories.

### Goal
Add a bounded integration smoke for one-command delivery success, transient
preflight resume and fail-closed stale/no-go behavior.

### Scope
- Integration fixtures and minimal test-only fake agent/reviewer surfaces.
- Release inventory/docs for the new smoke.

### Acceptance
- Success fixture использует temporary repo и local bare remote без внешней
  сети.
- Flow начинается с deliver-ready card и одного orchestration entrypoint.
- Final card, Git history, manifest, verdict, evidence и runner status
  согласованы.
- Fixture доказывает отсутствие stale tracked publish metadata и extra scope.
- Отдельный сценарий останавливается и возобновляется после transient preflight.
- Отдельный сценарий fail-closed при stale verdict или exhausted review budget.
- Smoke входит в release baseline с bounded runtime.

### Depends On
- `formalize-deliver-ready-card-contract`
- `add-retained-delivery-evidence`
- `add-remote-preflight-diagnostics-and-resume`
- `model-review-rescue-budget`

### Related
- `openspec/changes/archive/2026-08-02-prove-one-command-delivery-regression/`

## Archive
- `openspec/changes/archive/2026-08-02-prove-one-command-delivery-regression/`

## Verify
- 2026-08-02T00:13:17Z fast-forward validation:
  `bin/openspec validate prove-one-command-delivery-regression --strict`,
  `bin/openspec validate --all --strict`, `git diff --check` passed.
- 2026-08-02T00:18:51Z `python3 scripts/smoke-delivery-runner.py` passed.
- 2026-08-02T00:25:14Z `python3 scripts/run-release-baseline.py` passed
  all 27 steps, including `delivery runner one-command smoke`.
- 2026-08-02T00:22:01Z `python3 scripts/public-surface-scan.py` passed
  with 646 files and 0 findings.
- 2026-08-02T00:23:45Z `python3 scripts/public-surface-scan.py --history`
  passed with 646 files and 0 findings.
- 2026-08-02T00:28:29Z `./bin/openspec validate --all --strict` passed
  with 15 items.
- 2026-08-02T00:28:29Z `git diff --check` passed.

## Related
- `openspec/board/1.backlog/020-00-one-command-delivery-experience-epic.md`
- `scripts/smoke-delivery-runner.py`
- `scripts/smoke-delivery-manifest-derive.py`

## Result
implementation delivered, specs synced and OpenSpec change archived; awaiting
independent review

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-01T15:07:29Z добавлена как обязательный exit gate серии.
- 2026-08-01T21:24:05Z readiness pass после серии `010`: карточка переведена
  в `2.todo`, добавлен ordered Change 1 для package runner.
- 2026-08-02T00:13:17Z `$changerail-ff`: созданы OpenSpec artifacts для
  `prove-one-command-delivery-regression`, strict validation passed, карточка
  переведена в `3.inprogress`.
- 2026-08-02T00:29:34Z `$changerail-do`: добавлен one-command delivery
  regression smoke, обновлен release baseline inventory, specs synced,
  `prove-one-command-delivery-regression` archived; карточка оставлена в
  `3.inprogress` до independent review.
- 2026-08-02T00:50:09Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
