## ADDED Requirements

### Requirement: ChangeRail contract namespace
Public machine-readable contracts MUST use the `changerail.*` schema namespace
after the product rename.

#### Scenario: Review verdict is validated
- **WHEN** the review verdict helper validates a post-rename verdict
- **THEN** the verdict schema id is `changerail.review-verdict.v1`
- **AND** verdicts using `opsx.review-verdict.v1` are treated as pre-rename
  legacy artifacts

#### Scenario: Delivery manifest is validated
- **WHEN** the delivery manifest helper validates a post-rename manifest
- **THEN** the manifest schema id is `changerail.delivery-manifest.v1`

### Requirement: ChangeRail schema filenames
Tracked schema filenames MUST use the `changerail-*.schema.json` prefix after
the rename.

#### Scenario: Maintainer lists schemas
- **WHEN** a maintainer lists the tracked schema directory
- **THEN** review verdict, delivery manifest, evidence index, delivery run and
  review cycle history schemas use `changerail-*.schema.json` filenames
