# Изолировать npm stderr при проверке integrity

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Review
- Risk tier: `critical`
- Milestone audit: `yes`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `yes`
- Published investigation authorization: `none`

## Source
- Consumer verification exposed a false integrity mismatch when npm emitted a successful warning to stderr.

## Summary
`bin/verify-project` объединял stdout и stderr команды `npm view ... --json`.
Предупреждение npm перед корректным JSON делало payload невалидным и приводило
к ложному `registry integrity mismatch`. Verifier должен разбирать только
stdout успешной команды, сохраняя stderr для диагностики ошибки.

## Acceptance
- Корректный integrity JSON в stdout проходит проверку при ненулевом stderr и exit code 0.
- Реальное несовпадение integrity по-прежнему блокирует verification.
- При ненулевом exit code диагностическое сообщение сохраняет полезные stdout и stderr.
- Полный `smoke-verify-project` проходит с новым регрессионным сценарием.

## Change 1: `fix-npm-integrity-stderr-isolation`

### Why
Успешные npm diagnostics не являются частью machine-readable JSON payload.

### Goal
Разделить stdout/stderr в registry lookup и зафиксировать поведение smoke-тестом
и нормативным сценарием.

### Acceptance
- Все acceptance criteria карточки выполнены.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-08-18-fix-npm-integrity-stderr-isolation/`

## Change Set
- `fix-npm-integrity-stderr-isolation`

## Verify
- RED: `python3 scripts/smoke-verify-project.py --run-id red-npm-stderr-warning-2` -> 57/58 passed; only the new warning-isolation check failed.
- GREEN: `python3 scripts/smoke-verify-project.py --run-id green-npm-stderr-isolation` -> 59/59 passed.
- GREEN: real consumer `bin/verify-project` without npm log-level overrides -> 0 failures.
- GREEN: `bin/openspec validate --all --strict` -> 23/23 passed.
- GREEN: public-surface current-tree and history scans -> 972 files, 0 findings.
- HISTORICAL BLOCKER RESOLVED: the unrelated generated-bootstrap instruction
  budget was repaired later; current `python3 scripts/run-release-baseline.py`
  passes all `36/36` steps and Ruff passes inside the baseline.
- CURRENT: `python3 scripts/smoke-verify-project.py` passes `60/60` in the
  current branch baseline.

## Archive
- `openspec/changes/archive/2026-08-18-fix-npm-integrity-stderr-isolation/`

## Related
- `bin/verify-project`
- `scripts/smoke-verify-project.py`
- `openspec/specs/changerail-project-verification/spec.md`

## Result
Implementation is present in published commit `7aab1eb` and remains in the
current branch. A fresh critical final-certification review supplied the missing
canonical independent review receipt; no code reimplementation was required.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-18T09:25:00Z regression reproduced and implementation prepared.
- 2026-08-18T09:35:16Z scoped verification passed; unrelated baseline debt recorded.
- 2026-08-19T14:05:00Z board triage confirmed commit `7aab1eb` is an ancestor
  of the current published branch and the former baseline blocker is resolved;
  card remains in progress solely because the independent review receipt is
  missing.
- 2026-08-19T15:36:00Z package preparation declared a one-time critical
  final-certification milestone so the historical implementation receives a
  fresh semantic audit instead of a docs-only machine receipt.
- 2026-08-19T16:05:27Z independent critical final-certification review cycle 1
  returned `go`; one minor non-blocking evidence note was retained in ignored
  review evidence.
- 2026-08-19T16:08:35Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
