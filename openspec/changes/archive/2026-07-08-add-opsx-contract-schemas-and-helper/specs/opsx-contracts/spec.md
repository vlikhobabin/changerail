## ADDED Requirements

### Requirement: OPSX contract schemas
OPSX MUST provide tracked JSON schemas for review verdict, delivery manifest
and evidence index contracts using canonical `opsx.*` schema ids.

#### Scenario: Maintainer inspects contract schemas
- **WHEN** the `schemas/` directory is listed
- **THEN** schemas exist for `opsx.review-verdict.v1`,
  `opsx.delivery-manifest.v1` and `opsx.evidence-index.v1`

### Requirement: Review verdict helper validation
OPSX MUST provide a review-verdict helper that validates verdict shape,
cross-field consistency and optional working-tree freshness.

#### Scenario: Publish checks a verdict before staging
- **WHEN** publish validates `.runtime/opsx/reviews/<card-id>.json` with
  `--check-fresh`
- **THEN** validation fails unless the verdict schema is
  `opsx.review-verdict.v1`, the result is internally consistent and the
  recorded fingerprint matches the current working tree

### Requirement: Review verdict fingerprint
OPSX MUST provide a deterministic helper command that computes the review
freshness fingerprint from git HEAD, status and diff.

#### Scenario: Reviewer writes a verdict
- **WHEN** reviewer runs `bin/opsx-review-verdict fingerprint --workspace .`
- **THEN** the helper emits JSON containing the current head commit and
  `sha256:<hex>` diff fingerprint
