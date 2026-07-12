## Why

Delivery run status currently exposes wall time and coarse usage only, while the
runtime evidence that explains where time was spent stays in raw JSONL logs.
Maintainers need a public contract for best-effort performance fields before
runner and metrics behavior can rely on them.

## What Changes

- Extend the `changerail.delivery-run.v1` contract with optional performance
  summary fields for wall time, command counts, slow commands, event counts,
  review timing, publish timing and file-change counts.
- Define how runner-observed event timestamps and command durations are
  represented without making raw stdout/stderr logs public artifacts.
- Document which timing and usage fields are mandatory, optional or explicitly
  reported as `unknown`.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-contracts`: delivery-run status contract gains structured
  performance fields and best-effort timing semantics.
- `changerail-delivery-observability`: observability requirements include
  performance breakdown fields for delivery runs.

## Impact

- `schemas/changerail-delivery-run.schema.json`
- `docs/changerail-contracts.md`
- `openspec/specs/changerail-contracts/spec.md`
- `openspec/specs/changerail-delivery-observability/spec.md`
