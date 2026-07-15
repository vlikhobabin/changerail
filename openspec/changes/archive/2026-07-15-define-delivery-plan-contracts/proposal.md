## Why

Consumer projects that coordinate several independent ChangeRail workspaces need
a public queue contract before a runner can safely execute that queue. Today the
single-card delivery run contract is structured, but queue plans and aggregate
status are left to private supervisors.

## What Changes

- Add public Draft 2020-12 schemas for declarative queue plans and aggregate
  queue status records.
- Define public-safe plan fields for workspace aliases, consumer-root-relative
  workspace paths, cards, dependencies, waves, concurrency limits and per-card
  model/reasoning overrides.
- Define aggregate status fields for plan fingerprint, per-card states, child
  run record references, locks, terminal outcomes and push/no-push success.
- Extend schema smoke coverage so new contract schemas have positive and
  negative fixtures.
- Keep the existing single-card `changerail.delivery-run.v1` contract backward
  compatible.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-contracts`: add `changerail.delivery-plan.v1` and
  `changerail.delivery-plan-status.v1` public schema contracts.
- `changerail-delivery-runner`: specify the runner-visible queue plan and
  aggregate status contract consumed by plan-oriented commands.
- `changerail-delivery-observability`: specify queue metrics inputs from
  aggregate status and child delivery run records.

## Impact

- `schemas/changerail-delivery-plan.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `scripts/smoke-contract-schemas.py`
- `docs/changerail-contracts.md`
- `openspec/specs/changerail-contracts/spec.md`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `openspec/specs/changerail-delivery-observability/spec.md`
