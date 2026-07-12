# Исправить terminal outcome раннера при safety stop

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Тестовый запуск пакетного ChangeRail runner-а 2026-07-12:
  `runner-test-02-protect-public-data`.
- `.runtime/changerail/delivery-runs/runner-test-02-protect-public-data/status.json`
- `.runtime/changerail/delivery-runs/runner-test-02-protect-public-data/stdout.jsonl`
- `.runtime/changerail/reviews/protect-public-data-and-supply-chain.json`
- `bin/changerail-delivery-runner`
- `scripts/smoke-delivery-runner.py`

## Summary
Исправить машинный outcome delivery runner-а, чтобы safety stop после review
`no-go` не записывался как успешный `DELIVERED`.

Во время тестового прогона карточки `protect-public-data-and-supply-chain`
внутренний `$changerail-deliver` корректно остановил publish после второго
свежего `no-go` и написал в stdout safety stop. При этом child process завершился
с exit code `0`, а внешний `bin/changerail-delivery-runner` не увидел
authoritative structured terminal outcome и применил fallback:
`exit_code == 0 -> DELIVERED`.

В результате `status.json` получил:

```json
{
  "phase": "terminal",
  "result": "DELIVERED",
  "terminal_outcome": "DELIVERED",
  "process": {"exit_code": 0}
}
```

Это неверно для supervisor-а: payload не опубликован, карточка осталась в
`3.inprogress`, canonical review verdict свежий и имеет `result: no-go`.

## Findings
- `bin/changerail-delivery-runner` доверяет fallback-у по exit code, когда в
  Codex JSONL нет structured terminal outcome.
- `$changerail-deliver` может завершить safety stop текстовым сообщением и
  exit code `0`, не отдавая machine-readable `NO-GO` или `BLOCKED`.
- `status.json` после такого safety stop выглядит как успешный terminal
  outcome, что может ошибочно разрешить следующий card в batch.
- Существующие smoke checks покрывают structured `external-review/no-go`, но не
  покрывают child exit `0` + safety-stop/no-publish message + fresh no-go verdict.

## Acceptance
- Delivery runner никогда не записывает `DELIVERED`, если текущий card не
  опубликован и canonical fresh review verdict имеет `result: no-go`.
- Safety stop после исчерпания allowed review cycles получает machine-readable
  terminal outcome `NO-GO` или `BLOCKED` согласно documented contract, но не
  `DELIVERED`.
- `$changerail-deliver` и/или runner contract документируют, какой structured
  event обязан появляться в JSONL при safety stop, чтобы supervisor не зависел
  от свободного текста.
- Runner fallback по `exit_code == 0` применяется только когда нет признаков
  review-gated safety stop, stale/invalid/no-go verdict или blocked publish.
- `scripts/smoke-delivery-runner.py` содержит regression case: fake child exits
  `0`, сообщает safety stop после repeated `no-go`, а runner status получает
  non-delivered outcome и non-zero wrapper exit.
- Smoke покрывает, что batch не должен переходить к следующей карточке после
  такого outcome.
- Runtime `status.json`, printed `terminal_outcome` и wrapper exit code
  согласованы между собой.
- Документация runner-а и contract docs описывают этот case как safety stop.

## Change Set
- `fix-runner-review-safety-stop-outcome`

## Verify
- `$changerail-ff`: `openspec validate fix-runner-review-safety-stop-outcome --strict` passed.
- `$changerail-ff`: `openspec validate --all --strict` passed.
- `$changerail-ff`: `git diff --check` passed.
- `$changerail-do`: `python3 scripts/smoke-delivery-runner.py` passed with
  regression coverage for child exit `0` plus fresh `no-go` verdict fallback and
  sequential supervisor stop behavior.
- `$changerail-do`: `openspec validate fix-runner-review-safety-stop-outcome --strict` passed.
- `$changerail-do`: `openspec validate changerail-delivery-runner --strict` passed.
- `$changerail-do`: `openspec validate changerail-contracts --strict` passed.
- `$changerail-do`: `openspec validate --all --strict` passed.
- `$changerail-do`: `git diff --check` passed.
- `$changerail-do`: `python3 scripts/public-surface-scan.py` passed
  `(422 files scanned, 0 findings)`.

## Archive
- `openspec/changes/archive/2026-07-12-fix-runner-review-safety-stop-outcome/`

## Related
- `bin/changerail-delivery-runner`
- `scripts/smoke-delivery-runner.py`
- `docs/changerail-contracts.md`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `openspec/specs/changerail-contracts/spec.md`
- `skills/changerail-deliver/SKILL.md`
- `openspec/board/3.inprogress/protect-public-data-and-supply-chain.md`

## Result
implemented; awaiting independent review and publish

Published reviewed payload as `82f316ac62242726d93851193bb175deac1aa668`; push status `pending` on `main`/`origin`.

## Next
- done

## Change 1: `fix-runner-review-safety-stop-outcome`

### Why
Delivery runner supervisors need a reliable terminal outcome when `$changerail-deliver`
stops after a review-gated `no-go`. A child exit code of `0` is not enough to
prove publication when a fresh canonical verdict still blocks publish.

### Goal
Teach the runner contract and implementation to classify a successful child
exit with review-gated safety-stop evidence as `NO-GO` or `BLOCKED`, never
`DELIVERED`, and cover the case in the smoke suite.

### Scope
- Update delivery-runner outcome classification for fresh canonical `no-go`,
  stale/invalid verdict, and blocked publish evidence when no structured
  terminal event is present.
- Preserve existing authoritative JSONL terminal event behavior and the
  non-terminal tool-error success case.
- Add regression smoke coverage for child exit `0` plus repeated no-go
  safety-stop evidence, including single-card batch-stop semantics.
- Update public runner contract docs/specs and the deliver skill contract for
  the structured safety-stop event expectation.

### Acceptance
- Runner terminal `status.json`, printed `terminal_outcome` and wrapper exit code
  agree on a non-delivered outcome for the no-go safety-stop regression.
- The runner does not advance from the first card in a simulated batch after the
  non-delivered outcome.
- Existing structured JSONL terminal events remain authoritative and ordered.
- Documentation and specs describe the structured event or fallback evidence
  contract without relying on arbitrary free-text log parsing.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-12-fix-runner-review-safety-stop-outcome/`

## Log
- 2026-07-12T17:36:00Z card created from observed runner mismatch: safety stop
  after fresh review `no-go` was recorded as `DELIVERED` in delivery-run status.
- 2026-07-12T19:39:25Z `$changerail-ff` accepted scope, created one ordered
  change, and moved card to `2.todo`.
- 2026-07-12T19:42:19Z `$changerail-ff` completed OpenSpec artifacts and moved
  card to `3.inprogress`.
- 2026-07-12T19:47:10Z `$changerail-do` implemented runner fallback, smoke
  regression coverage, docs/spec/skill updates and verification; preparing
  OpenSpec archive before review.
- 2026-07-12T19:47:48Z `$changerail-do` archived
  `fix-runner-review-safety-stop-outcome`; card remains in `3.inprogress` for
  independent review.
- 2026-07-12T19:55:11Z publish finalized card into `4.done` with commit `82f316ac62242726d93851193bb175deac1aa668` and push status `pending`.
