## Why

Runtime logs and latest review verdict are insufficient for OPSX operations:
они не сохраняют историю review cycles и плохо подходят для метрик. Метрики
должны читаться из машинных run records и review evidence, а не из свободного
текста логов.

## What Changes

- Сохранять review-cycle evidence history без потери предыдущего `no-go`, при
  этом latest canonical verdict остается совместимым с publish freshness gate.
- Добавить tracked metrics tool, который читает structured run records и
  review-cycle evidence.
- Печатать per-run и aggregate результаты: first-pass go rate, findings по
  severity, acceptance outcomes, wall-time и доступный token usage.
- Поддержать CSV output и явное отображение отсутствующих optional fields.
- Добавить worked operational flow `over-claim -> no-go -> scoped rescue ->
  re-review -> go -> pub` в durable methodology/docs.

## Capabilities

### New Capabilities
- `opsx-delivery-observability`: run record metrics, review-cycle history and
  CSV reporting behavior.

### Modified Capabilities
- `opsx-contracts`: добавить review-cycle evidence contract and metrics inputs.
- `opsx-agent-methodology`: описать operational feedback loop and scoped rescue
  flow.

## Impact

- new metrics helper under `bin/` or `scripts/`
- review-cycle evidence schema/docs
- docs and methodology updates
- smoke tests for aggregate metrics and CSV rendering
