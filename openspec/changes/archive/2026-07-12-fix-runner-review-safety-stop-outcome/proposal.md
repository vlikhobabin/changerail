## Why

Delivery runner сейчас может ошибочно записать `DELIVERED`, если вложенный
`$changerail-deliver` завершился с exit code `0`, но фактически остановился на
review-gated safety stop после свежего `no-go`. Это ломает supervisor-семантику:
batch может перейти к следующей карточке, хотя текущая не опубликована.

## What Changes

- Runner получает fail-closed fallback для review-gated safety stop-ов, когда в
  JSONL нет authoritative terminal event.
- Fallback учитывает canonical review verdict для текущей card и не записывает
  `DELIVERED` при свежем `result: no-go`, stale/invalid verdict или blocked
  publish evidence.
- Smoke suite получает regression case для child exit `0` + safety-stop/no-go
  evidence и проверяет, что simulated batch не переходит к следующей карточке.
- Public docs, specs и `changerail-deliver` contract фиксируют structured
  terminal event expectation и runner fallback boundary.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-delivery-runner`: terminal outcome fallback for review-gated safety
  stops changes observable runner behavior.
- `changerail-contracts`: public delivery-run contract docs describe the
  structured event and fallback evidence boundary.

## Impact

- `bin/changerail-delivery-runner`
- `scripts/smoke-delivery-runner.py`
- `docs/changerail-contracts.md`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `openspec/specs/changerail-contracts/spec.md`
- `skills/changerail-deliver/SKILL.md`
