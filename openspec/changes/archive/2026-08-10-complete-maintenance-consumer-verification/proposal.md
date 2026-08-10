## Why

Opted-in maintenance consumers can currently pass `verify-project` even when
the latest public maintenance quality and proposal-decision schemas are not
reachable. That leaves generated or stale consumer wiring looking healthy while
part of the documented maintenance contract is absent.

## What Changes

- Add `changerail-maintenance-quality-rollup.schema.json` and
  `changerail-maintenance-proposal-decision.schema.json` to the maintenance
  schema inventory required by `verify-project`.
- Extend POSIX and generated-copy verification smoke coverage for complete,
  missing and stale maintenance contract surfaces.
- Keep the current no-scan verifier boundary: `verify-project` checks
  wiring/contracts but does not run the full maintenance scan.
- Preserve opt-out behavior for consumers with no maintenance policy, helper
  wiring or generated maintenance ownership declaration.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-project-verification`: opted-in maintenance verification requires
  every tracked maintenance schema, including quality rollup and proposal
  decision contracts.

## Impact

- Affected files: `bin/verify-project`, `scripts/smoke-verify-project.py`,
  `scripts/smoke-bootstrap-project.py` where expected maintenance schema checks
  are asserted, and project-verification specs.
- Consumer impact is fail-closed but only for repositories that explicitly opt
  in to maintenance wiring.
