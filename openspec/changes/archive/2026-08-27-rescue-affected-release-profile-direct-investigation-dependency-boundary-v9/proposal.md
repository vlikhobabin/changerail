## Why

Published affected v8 задаёт exact implementation dependency set без прямой
зависимости от investigation id, тогда как deterministic preflight требует
такую зависимость для bounded investigation authorization. Clean v8 поэтому не
может пройти оба fail-closed контракта и должен остаться terminal unpublished.

## What Changes

- Фиксируется terminal forensic-only статус unpublished v8 и точная причина
  preflight stop без чтения или импорта его payload/runtime evidence.
- Исполняемая v8 lineage заменяется clean v9 order: docs-only rescue decision,
  отдельная authorization v9, clean implementation v9, затем certification.
- Future implementation v9 получает exact прямую зависимость и от этой
  investigation decision, и от отдельно опубликованной authorization v9.
- Сохраняются 499 production LOC ceiling, protocol allowance и весь
  accumulated affected-profile fail-closed contract.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-release-ci`: добавляет нормативную v9 replacement lineage,
  direct-investigation dependency boundary и terminal-v8 no-reuse contract.

## Impact

Change docs-only: board card, same-slug OpenSpec artifacts и main
`changerail-release-ci` specification. Production, tests, CI, schemas,
dependencies, runtime authority, v9 successors и certification не изменяются
и не создаются.
