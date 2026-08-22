## Why

Отдельные runner processes, preflights, recoveries и review cycles сейчас не
образуют одной проверяемой истории карточки. Без stable episode/attempt lineage
невозможно связать блокировку, восстановление, rescue и publish, не прибегая к
raw logs и догадкам по timestamps.

## What Changes

- Добавить stable `episode_id` и уникальный `attempt_id` для single-card и queue
  execution attempts с explicit parent/previous linkage.
- Классифицировать attempt kinds и bounded terminal/blocker outcomes для
  preflight, delivery, recovery, review, rescue и publish.
- Сохранять агрегированные phase durations, usage и tool/command counts даже
  при усечении bounded detail samples; явно записывать sampling limits.
- Связать append-only review history и publish result с тем же episode без
  копирования findings, prompts или payload bodies в run status.
- Обеспечить schema-compatible fallback: legacy v1 records без lineage остаются
  читаемыми как отдельные episodes с unknown полями.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-delivery-runner`: runtime records получают recovery-aware
  episode/attempt lineage и полные aggregate counters.
- `changerail-contracts`: status schemas закрепляют identity, attempt kinds,
  linkage, bounded events и sampling metadata.
- `changerail-delivery-observability`: retained telemetry связывает полный
  lifecycle карточки без raw agent logs.

## Impact

- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `schemas/changerail-review-cycle-history.schema.json`
- delivery-runner and contract smokes
