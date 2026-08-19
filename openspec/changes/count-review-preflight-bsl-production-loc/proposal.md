## Why

Large 1C BSL modules currently produce `added_production_loc = 0` because
`.bsl` is absent from the deterministic production source classifier. That
creates a false-green path around the investigation guard for production code.

## What Changes

- Count added `.bsl` lines as production complexity only when the path is
  classified as production source by the declared source-classification
  contract.
- Keep `.bsl` under existing non-production roots such as `test`, `tests`,
  `fixtures` and `examples` out of `added_production_loc`.
- Add a RED/GREEN focused smoke that reproduces the current false-negative with
  synthetic BSL files and proves the fixed counting behavior.
- Preserve existing Python, Go, JavaScript and executable-helper production
  classification semantics.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-contracts`: deterministic review preflight counts declared
  production BSL source and excludes non-production BSL fixtures.

## Impact

Affected files include `scripts/changerail_review_preflight.py`,
`scripts/smoke-review-preflight.py`, contract docs and the
`changerail-contracts` spec. No real 1C configuration exports or customer data
are added; smoke fixtures are generated synthetically in temporary
repositories.
