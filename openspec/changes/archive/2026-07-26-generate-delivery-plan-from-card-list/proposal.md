## Why

Typical serial delivery of several board cards should not require hand-writing
the full `changerail.delivery-plan.v1` JSON. Operators need a small helper that
generates a valid plan from ordered card paths and optional dependencies.

## What Changes

- Add a `generate-plan` command to `bin/changerail-delivery-runner`.
- Accept repeatable workspace declarations, ordered card paths and optional
  dependency declarations.
- Emit schema-compatible `changerail.delivery-plan.v1` JSON to stdout or an
  explicit output path.
- Validate the generated plan through the same schema-backed path used by
  existing `plan` and `preflight-plan` commands.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-delivery-runner`: provide plan generation from ordered card lists.
- `changerail-contracts`: document that generated plans remain the canonical
  `changerail.delivery-plan.v1` contract, not a separate format.

## Impact

- `bin/changerail-delivery-runner`
- `scripts/smoke-delivery-runner.py`
- `docs/changerail-contracts.md`
- `docs/consumer-adoption-runbook.md`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `openspec/specs/changerail-contracts/spec.md`
