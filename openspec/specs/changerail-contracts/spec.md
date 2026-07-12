# changerail-contracts Specification

## Purpose
Зафиксировать публичные wire contracts ChangeRail для review, delivery и evidence
handoff, а также helper-поведение для review-verdict validation и freshness
fingerprint.
## Requirements
### Requirement: ChangeRail contract schemas
ChangeRail MUST provide tracked JSON schemas for review verdict, delivery manifest
and evidence index contracts using canonical `changerail.*` schema ids.

#### Scenario: Maintainer inspects contract schemas
- **WHEN** the `schemas/` directory is listed
- **THEN** schemas exist for `changerail.review-verdict.v1`,
  `changerail.delivery-manifest.v1` and `changerail.evidence-index.v1`

### Requirement: Review verdict helper validation
ChangeRail MUST provide a review-verdict helper that validates verdict shape,
cross-field consistency and optional working-tree freshness.

#### Scenario: Publish checks a verdict before staging
- **WHEN** publish validates `.runtime/changerail/reviews/<card-id>.json` with
  `--check-fresh`
- **THEN** validation fails unless the verdict schema is
  `changerail.review-verdict.v1`, the result is internally consistent and the
  recorded fingerprint matches the current working tree

### Requirement: Review independence attestation
Review verdicts MUST include a machine-checkable reviewer independence
attestation that states whether the reviewer used a fresh context and did not
plan or implement the reviewed payload.

#### Scenario: Reviewer writes a go verdict
- **WHEN** a reviewer writes `.runtime/changerail/reviews/<card-id>.json`
- **THEN** the `reviewer` object includes an independence attestation with
  `fresh_context: true`, `did_not_plan_or_implement: true` and a non-empty
  basis

#### Scenario: Publish validates a verdict without attestation
- **WHEN** `bin/changerail-review-verdict validate --check-fresh` checks a
  verdict whose reviewer independence attestation is missing or false
- **THEN** validation fails before publish can stage files

### Requirement: Independence limits are explicit
Review verdict docs MUST state that helper validation checks reviewer
attestation and working-tree freshness, but cannot by itself prove the real
identity or full memory boundary of an external agent session.

#### Scenario: Maintainer reads review contract docs
- **WHEN** a maintainer reads the review verdict reference
- **THEN** the document distinguishes machine-checked attestation from
  operator-enforced session independence

### Requirement: Review verdict fingerprint
ChangeRail MUST provide a deterministic helper command that computes the review
freshness fingerprint from git HEAD, status, tracked diff and untracked
non-ignored file content.

#### Scenario: Reviewer writes a verdict
- **WHEN** reviewer runs `bin/changerail-review-verdict fingerprint --workspace .`
- **THEN** the helper emits JSON containing the current head commit and
  `sha256:<hex>` diff fingerprint

#### Scenario: Untracked deliverable content changes
- **WHEN** an untracked non-ignored file's content changes without changing its
  path
- **THEN** the helper emits a different `sha256:<hex>` diff fingerprint

#### Scenario: Ignored runtime content changes
- **WHEN** an ignored file such as `.runtime/changerail/reviews/<card-id>.json` is
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
ChangeRail MUST define a public `changerail.delivery-run.v1` contract for machine-readable
delivery run status and terminal outcomes.

#### Scenario: Runner writes status
- **WHEN** the delivery runner writes
  `<workspace>/.runtime/changerail/delivery-runs/<run-id>/status.json` by default
- **THEN** the JSON uses `changerail.delivery-run.v1` and includes card, phase,
  result, timestamps and command metadata
- **AND** the record includes `commit` when workspace `HEAD` is available

#### Scenario: Usage is unavailable
- **WHEN** the runner cannot observe token usage from the provider output
- **THEN** the run record explicitly reports usage as unavailable instead of
  guessing values

### Requirement: Review cycle evidence contract
ChangeRail MUST define runtime review-cycle evidence that can retain previous review
results while leaving `.runtime/changerail/reviews/<card-id>.json` as the latest
canonical publish gate verdict.

#### Scenario: Latest verdict remains canonical
- **WHEN** publish validates a review verdict
- **THEN** it continues to validate `.runtime/changerail/reviews/<card-id>.json`
  against `changerail.review-verdict.v1`

#### Scenario: Metrics reads historical cycles
- **WHEN** review-cycle evidence exists for prior cycles
- **THEN** metrics can count historical findings without modifying the latest
  canonical verdict
- **AND** each historical cycle retains finding details or an immutable
  per-cycle verdict snapshot path

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
