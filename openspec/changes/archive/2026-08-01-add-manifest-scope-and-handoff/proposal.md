## Why

Delivery and publish still rely on manual, rename-aware comparison between the
delivery manifest and the actual Git scope. Review and publish handoff also lack
a compact machine-readable summary of verification, review and final card state,
so operators must reconstruct the delivery outcome from card text and ignored
runtime artifacts.

## What Changes

- Add a delivery manifest scope reconciliation command that compares claimed
  `committable_paths` with both working-tree status and staged index status.
- Make scope reconciliation NUL-safe and operation-aware for add, modify,
  delete and rename entries, including paths that require byte-preserving
  filesystem round trips.
- Report missing, extra and mismatched paths explicitly, while excluding ignored
  runtime paths from committable scope.
- Extend delivery manifests with concise verification, review and final card
  state summaries for review/publish handoff.
- Add schema and smoke coverage that rejects a false green when an extra staged
  path is outside the manifest scope.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-contracts`: add manifest scope reconciliation and handoff summary
  requirements to the delivery manifest contract.

## Impact

- `scripts/changerail_delivery_manifest.py`
- `schemas/changerail-delivery-manifest.schema.json`
- `scripts/smoke-delivery-manifest.py`
- `scripts/smoke-delivery-manifest-derive.py`
- `scripts/smoke-contract-schemas.py`
- `docs/changerail-contracts.md`
- `skills/changerail-do/SKILL.md`
- `skills/changerail-review/SKILL.md`
- `skills/changerail-pub/SKILL.md`
