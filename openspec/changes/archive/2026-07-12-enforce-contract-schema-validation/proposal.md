## Why

Delivery manifest и review verdict helpers публикуют JSON Schemas как
canonical contracts, но validators вручную повторяли только часть этих schemas.
Из-за этого malformed runtime contracts могли проходить helpers и publish gates,
даже когда нарушали required schema shape.

## What Changes

- Валидировать delivery manifest и review verdict documents по tracked Draft
  2020-12 JSON Schemas, включая `format`, `additionalProperties`, conditional
  required fields и nested type rules.
- Держать ChangeRail semantic invariants отдельно от schema validation,
  например verdict result consistency и review freshness.
- Гарантировать, что CLI helpers и smoke tests используют один schema
  validation path.
- Добавить negative fixtures для malformed `go` verdicts и manifest documents,
  чтобы schema drift fail-closed со structured diagnostics.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-contracts`: helper validation должен enforce canonical schemas до
  применения ChangeRail-specific semantic rules.

## Impact

- `scripts/changerail_delivery_manifest.py`
- `scripts/changerail_review_verdict.py`
- `scripts/smoke-delivery-manifest-derive.py`
- `scripts/smoke-review-verdict-validation.py`
- `docs/changerail-contracts.md`
- `skills/changerail-review/references/changerail-review-verdict.md`
- `openspec/specs/changerail-contracts/spec.md`
