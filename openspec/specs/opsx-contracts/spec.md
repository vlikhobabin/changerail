# opsx-contracts Specification

## Purpose
Зафиксировать публичные wire contracts OPSX для review, delivery и evidence
handoff, а также helper-поведение для review-verdict validation и freshness
fingerprint.

## Requirements
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
freshness fingerprint from git HEAD, status, tracked diff and untracked
non-ignored file content.

#### Scenario: Reviewer writes a verdict
- **WHEN** reviewer runs `bin/opsx-review-verdict fingerprint --workspace .`
- **THEN** the helper emits JSON containing the current head commit and
  `sha256:<hex>` diff fingerprint

#### Scenario: Untracked deliverable content changes
- **WHEN** an untracked non-ignored file's content changes without changing its
  path
- **THEN** the helper emits a different `sha256:<hex>` diff fingerprint

#### Scenario: Ignored runtime content changes
- **WHEN** an ignored file such as `.runtime/opsx/reviews/<card-id>.json` is
  added or changed
- **THEN** the helper emits the same `sha256:<hex>` diff fingerprint for the
  otherwise unchanged working tree

### Requirement: Delivery manifest file operations
Delivery manifests MUST represent card-owned file operations well enough for
publish to build a complete staging proposal for additions, modifications,
deletions and renames.

#### Scenario: Board card move is claimed completely
- **WHEN** a card moves from one board column path to another
- **THEN** the manifest records the source path and target path or equivalent
  structured operation data so publish can stage both sides of the move

#### Scenario: Deleted path remains in scope
- **WHEN** delivery removes a card-owned tracked file
- **THEN** the manifest records the deleted path as a committable path instead
  of only recording remaining files

### Requirement: Delivery run record contract
OPSX MUST define a public `opsx.delivery-run.v1` contract for machine-readable
delivery run status and terminal outcomes.

#### Scenario: Runner writes status
- **WHEN** the delivery runner writes
  `<workspace>/.runtime/opsx/delivery-runs/<run-id>/status.json` by default
- **THEN** the JSON uses `opsx.delivery-run.v1` and includes card, phase,
  result, timestamps and command metadata
- **AND** the record includes `commit` when workspace `HEAD` is available

#### Scenario: Usage is unavailable
- **WHEN** the runner cannot observe token usage from the provider output
- **THEN** the run record explicitly reports usage as unavailable instead of
  guessing values

### Requirement: Review cycle evidence contract
OPSX MUST define runtime review-cycle evidence that can retain previous review
results while leaving `.runtime/opsx/reviews/<card-id>.json` as the latest
canonical publish gate verdict.

#### Scenario: Latest verdict remains canonical
- **WHEN** publish validates a review verdict
- **THEN** it continues to validate `.runtime/opsx/reviews/<card-id>.json`
  against `opsx.review-verdict.v1`

#### Scenario: Metrics reads historical cycles
- **WHEN** review-cycle evidence exists for prior cycles
- **THEN** metrics can count historical findings without modifying the latest
  canonical verdict
- **AND** each historical cycle retains finding details or an immutable
  per-cycle verdict snapshot path
