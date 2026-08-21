# Preserve NO-GO with malformed terminal marker

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Review
- Risk tier: `ordinary`
- Review effort: `high`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Summary
Сохранить schema-valid canonical `no-go` как консервативный terminal outcome,
когда child одновременно оставляет распознаваемый `BLOCKED` marker с
невалидным `terminal_reason`.

## Acceptance
- Schema-valid unpublished `no-go` заменяет только диагностический
  `BLOCKED/malformed_terminal_reason` и дает terminal `NO-GO`.
- Malformed terminal marker без валидного negative verdict остается
  `BLOCKED/malformed_terminal_reason`.
- Stale/invalid `go` не может заменить malformed marker положительным исходом
  или разрешить публикацию.
- Delivery-runner smoke и полный release baseline проходят.

## Change Set
- `preserve-no-go-with-malformed-terminal-marker`

## Change 1: `preserve-no-go-with-malformed-terminal-marker`

### Goal
Уточнить приоритет canonical negative review evidence над диагностическим
malformed child marker без ослабления остальных fail-closed путей.

### Depends On
- none

### Size Budget
- At most 300 added production LOC.

## Verify
- `python3 scripts/smoke-delivery-runner.py`
- `bin/openspec validate --all --strict`
- `python3 scripts/run-release-baseline.py`
- `git diff --check`
- fresh independent ordinary/high review

## Next
- done

## Log
- 2026-08-21: reproduced aggregate misclassification after a final canonical no-go and malformed child terminal reason.
- 2026-08-21: implemented the narrow negative-evidence override; focused smoke, strict OpenSpec and the 36-step release baseline passed.
- 2026-08-21T15:37:42Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.

## Result
Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.
