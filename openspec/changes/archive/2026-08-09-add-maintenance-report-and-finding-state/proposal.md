## Why

Maintenance scan output уже полезен для gates, но consumer-ам нужен
нормализованный lifecycle report со стабильной identity findings, отдельным
evidence change detection и bounded ignored state. Без этого слоя scheduler-ы
и agents будут либо ключеваться на volatile messages, либо копировать raw
detector evidence в tracked surfaces.

## What Changes

- Добавить normalized `changerail.maintenance-report.v1` contract, который
  строится только из complete schema-valid scan reports.
- Добавить finding identity и evidence fingerprint semantics, где volatile text,
  timestamps и absolute workspace root не участвуют в identity.
- Добавить fail-closed sanitation для unsafe paths и secret-like evidence до
  публикации lifecycle output.
- Добавить atomic ignored runtime state под `.runtime/changerail/maintenance/`
  с явными continuity limits для ephemeral runners.
- Добавить CLI coverage для lifecycle report preview и explicit state writes.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-repository-knowledge`: добавить maintenance lifecycle report,
  fingerprint и runtime state requirements поверх существующих scan/detector
  contracts.

## Impact

- `schemas/` получает public maintenance lifecycle report/state schema.
- `scripts/changerail_repository_knowledge.py` и `bin/changerail-maintenance`
  получают normalization и explicit state-write behavior.
- Repository knowledge smoke fixtures покрывают identity stability,
  evidence-change и corrupt-state handling.
