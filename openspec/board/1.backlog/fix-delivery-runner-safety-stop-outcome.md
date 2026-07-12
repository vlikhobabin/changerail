# Исправить terminal outcome раннера при safety stop

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

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
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `bin/changerail-delivery-runner`
- `scripts/smoke-delivery-runner.py`
- `docs/changerail-contracts.md`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `skills/changerail-deliver/SKILL.md`
- `openspec/board/3.inprogress/protect-public-data-and-supply-chain.md`

## Result
not started

## Next
- Triage whether the fix belongs in `$changerail-deliver`, the outer delivery
  runner, or both, then create ordered OpenSpec changes.

## Log
- 2026-07-12T17:36:00Z card created from observed runner mismatch: safety stop
  after fresh review `no-go` was recorded as `DELIVERED` in delivery-run status.
