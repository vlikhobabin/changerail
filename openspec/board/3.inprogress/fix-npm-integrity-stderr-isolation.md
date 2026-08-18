# Изолировать npm stderr при проверке integrity

## Status
3.inprogress

## Owner
Codex delivery worker

## OpenSpec Stage
implemented; awaiting independent review

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
- BASELINE BLOCKER: `python3 scripts/run-release-baseline.py` stopped at the
  unchanged generated-bootstrap fixture because `AGENTS.md` reaches 27,866 of
  32,768 bytes and crosses the 85% warning threshold. The owning source and
  template are unchanged from `origin/main`; resolve in a separate change.
- NOT RUN: Ruff is unavailable in the selected Python environment.

## Archive
- `openspec/changes/archive/2026-08-18-fix-npm-integrity-stderr-isolation/`

## Related
- `bin/verify-project`
- `scripts/smoke-verify-project.py`
- `openspec/specs/changerail-project-verification/spec.md`

## Result
Implementation and scoped verification complete. Independent review remains;
the unrelated instruction-budget baseline blocker is recorded above.

## Next
- Run full verification, commit the scoped branch, then request independent review before PR.

## Log
- 2026-08-18T09:25:00Z regression reproduced and implementation prepared.
- 2026-08-18T09:35:16Z scoped verification passed; unrelated baseline debt recorded.
