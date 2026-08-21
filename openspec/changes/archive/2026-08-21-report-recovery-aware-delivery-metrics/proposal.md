## Why

Текущий metrics report считает preflight-only records как delivery runs и
присоединяет latest card review history к несвязанным ранним запускам. После
появления episode lineage отчет должен агрегировать попытки по реальной
delivery episode и корректно показывать recovery cost и first-pass outcomes.

## What Changes

- Собирать schema-valid attempts по `episode_id` и отделять preflight-only
  records от delivery denominators.
- Присоединять review cycles и publish result только по explicit episode/attempt
  linkage, а не по одному card id.
- Рассчитывать episode wall/active/wait/operator-wait durations, token и tool
  totals, recovery counts и final outcome с явным `unknown` для отсутствующих
  optional данных.
- Добавить text/JSON/CSV fields и fixtures для one-pass, resumed, rescued,
  abandoned и legacy runs.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-delivery-observability`: metrics становятся episode-aware и
  исключают preflight-only записи из delivery success/review rates.

## Impact

- `bin/changerail-delivery-metrics`
- `scripts/smoke-delivery-metrics.py`
- metrics documentation and examples
- зависит от `record-recovery-aware-delivery-episodes`
