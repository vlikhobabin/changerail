## Why

Machine-readable contract ids, helper names and runtime directories currently
keep the old `opsx` namespace even when the product is renamed. Leaving them in
place would make review evidence, delivery status and public schemas inconsistent
with the new ChangeRail identity.

## What Changes

- **BREAKING**: Rename public schema ids from `opsx.*.v1` to
  `changerail.*.v1`.
- **BREAKING**: Rename schema filenames from `opsx-*.schema.json` to
  `changerail-*.schema.json`.
- Rename helper wrappers and scripts from `opsx-*`/`opsx_*` to
  `changerail-*`/`changerail_*`.
- Change default ignored runtime paths from `.runtime/opsx/...` to
  `.runtime/changerail/...`.
- Rename ChangeRail-owned environment variables such as smoke/fake-mode flags.
- Update compatibility and migration docs to identify the contract namespace
  change as breaking.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-contracts`: rename review verdict, delivery manifest, evidence index,
  delivery run and review history schema ids and files.
- `changerail-delivery-runner`: update runner prompts, status schema and runtime
  defaults for the ChangeRail namespace.
- `changerail-delivery-observability`: update delivery metrics inputs and review-cycle
  history paths for the ChangeRail runtime namespace.

## Impact

- `schemas/opsx-*.schema.json`
- `bin/opsx-review-verdict`, `bin/opsx-delivery-runner`,
  `bin/opsx-delivery-metrics`
- `scripts/opsx_*` helpers and smoke tests
- `.runtime/opsx` default path references
- `docs/opsx-contracts.md` and related skill reference docs
- Consumer projects that validate old `opsx.*` schema ids need migration.
