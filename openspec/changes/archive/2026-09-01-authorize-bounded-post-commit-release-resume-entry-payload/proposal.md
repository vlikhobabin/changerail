## Why

Published investigation требует отдельный clean tracked authorization source,
прежде чем exact post-commit release resume successor сможет пройти bounded
review выше ordinary production LOC limit. Inline decision или неполная связь
между investigation, authorization-card и successor должны оставаться
недействительными.

## What Changes

- Публикуется docs/OpenSpec-only authorization-card, связанная с exact
  investigation и exact successor через нормативный six-field object.
- Фиксируются measured predecessor baseline `299`, successor forecast
  `359..399`, planned increment не более `100` counted LOC и hard ceiling
  `400`; measurement `401+` fail closed для split или нового investigation.
- Protocol allowance остаётся `false`; новая schema, provider, credential,
  workflow или mutation authority не разрешаются.
- Canonical deterministic preflight обязан проверять exact six-field values,
  обе reciprocal investigation dependency edges и exact successor id/path и
  fail closed при missing, unpublished, extra или mismatched данных.
- Successor card и её two-field authorization reference остаются неизменными до
  публикации authorization-card; production/runtime/test implementation и
  release mutation не входят в change.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-release-discipline`: добавить нормативный bounded authorization
  source для exact first-stable post-commit resume investigation/successor
  chain и её fail-closed consumption boundary.

## Impact

Delivery затрагивает только authorization board card, OpenSpec artifacts и
последующую синхронизацию одного delta requirement в
`openspec/specs/changerail-release-discipline/spec.md`. Successor card,
production/runtime/test code, schemas, providers, credentials, workflows,
release-card, tag, GitHub Release, assets и release mutation не изменяются.
