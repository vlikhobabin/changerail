# Доказать one-command delivery интеграционным regression smoke

## Status
1.backlog

## Owner
ChangeRail core

## OpenSpec Stage
story

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
- none yet

## Verify
- Новый end-to-end smoke.
- Полный `python3 scripts/run-release-baseline.py`.
- Public-surface current/history scans.

## Related
- `openspec/board/1.backlog/020-00-one-command-delivery-experience-epic.md`
- `scripts/smoke-delivery-runner.py`
- `scripts/smoke-delivery-manifest-derive.py`

## Result
not started

## Next
- После `020-04` выполнить `$changerail-ff` для этой карточки.

## Log
- 2026-08-01T15:07:29Z добавлена как обязательный exit gate серии.
