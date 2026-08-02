## Why

Серия `040-native-windows-implementation` была provisional до завершения
research серии `030`. После выбора architecture decision нужно перепланировать
epic и executable cards, чтобы implementation backlog отражал один default
path, bounded fallback-и, ownership rules и verification floor.

## What Changes

- Переписать `040` epic из provisional outline в refreshed implementation plan
  against `030-03`.
- Обновить cards `040-01`..`040-05`: scope, acceptance, dependencies,
  Change Set handoff, verification expectations и delivery order.
- Указать, какие Windows pieces должны быть implemented, verified, smoked and
  proved end-to-end в отдельных card-owned changes.
- Сохранить implementation code changes вне этой карточки.

## Capabilities

### New Capabilities
- `changerail-windows-implementation-series`: planning contract for the
  refreshed native Windows implementation series after `030-03`.

### Modified Capabilities
- none

## Impact

- Updates only board planning files under `openspec/board/1.backlog/` and the
  active `030-03` card handoff.
- Produces no runtime behavior change by itself.
- Prepares the next deliverable series for `ff -> do -> review -> pub`.
