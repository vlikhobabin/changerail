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

### Requirement: Delivery manifest derivation helper
ChangeRail MUST provide a helper command that can derive a delivery manifest
from a board card and the current workspace state.
Delivery manifest derivation MUST sanitize repository identity before writing it
to runtime records.

#### Scenario: Delivery derives a card manifest
- **WHEN** an operator runs the manifest helper for a board card
- **THEN** the helper derives card id, card path, card status, ordered changes,
  archived change paths and dirty committable paths
- **AND** it excludes ignored runtime verdict and manifest paths from
  `committable_paths`

#### Scenario: Reviewer inspects derived staging plan
- **WHEN** a derived manifest is passed to `staging-plan`
- **THEN** the output is a deterministic list of repository-relative paths that
  can be audited before publish staging

#### Scenario: Manifest redacts credential-bearing repository identity
- **WHEN** delivery manifest derivation reads an HTTPS remote containing URL
  userinfo, password or token-like query values
- **THEN** the manifest repository identity excludes raw userinfo, password,
  query and fragment values
- **AND** the identity retains non-sensitive scheme, host and repository path
  metadata when available

#### Scenario: Manifest redacts SCP-style SSH userinfo
- **WHEN** delivery manifest derivation reads an SCP-style SSH remote such as
  `user@example.invalid:org/repo.git`
- **THEN** the manifest repository identity excludes the raw SSH username
- **AND** it retains non-sensitive host and repository path metadata

### Requirement: Точный вывод delivery manifest paths
Delivery manifest derivation MUST использовать machine-readable git status data
и MUST записывать точные repository-relative paths для card-owned additions,
modifications, deletions и renames без shell quoting artifacts.

#### Scenario: Manifest точно записывает допустимые символы path
- **WHEN** manifest derivation видит changed paths со spaces, quotes, Unicode
  characters или literal ` -> ` text
- **THEN** `committable_paths` записывает repository-relative paths без
  добавленных quotes, lossy splitting или arrow-based rewrite

#### Scenario: Manifest сохраняет non-UTF-8 path bytes
- **WHEN** manifest derivation видит repository path с valid non-UTF-8 bytes в
  Linux workspace
- **THEN** JSON output остается valid UTF-8 и сохраняет path так, что
  filesystem byte round-trip через `os.fsencode` восстанавливает исходные bytes

#### Scenario: Manifest записывает source и target для rename
- **WHEN** manifest derivation видит card-owned rename
- **THEN** manifest записывает `operation: rename`, `source_path` и
  `target_path`

#### Scenario: Manifest записывает deleted path
- **WHEN** manifest derivation видит card-owned delete
- **THEN** manifest записывает `operation: delete` и `source_path` для removed
  path

### Requirement: Консервативный untracked manifest scope
Delivery manifest derivation MUST NOT включать directory-wide untracked path в
`committable_paths`, когда такой path может stage-ить unrelated files.

#### Scenario: Untracked directory содержит несколько files
- **WHEN** manifest derivation видит untracked files в одном directory
- **THEN** `committable_paths` содержит каждый точный file path вместо parent
  directory

#### Scenario: Untracked path нельзя безопасно перечислить
- **WHEN** manifest derivation не может представить untracked directory или
  non-regular path как точные file paths
- **THEN** helper validation завершается fail до записи staging proposal

### Requirement: Canonical schema-backed validation для contracts
ChangeRail helper validation для delivery manifests и review verdicts MUST
валидировать указанный документ по tracked canonical Draft 2020-12 JSON Schema
до применения ChangeRail-specific semantic rules.

#### Scenario: Manifest нарушает canonical schema
- **WHEN** `scripts/changerail_delivery_manifest.py validate --json` получает
  manifest с unknown fields, invalid date-time formats, wrong nested types или
  missing conditional operation fields
- **THEN** helper завершается non-zero со structured diagnostic и не сообщает,
  что manifest valid

#### Scenario: Verdict нарушает canonical schema
- **WHEN** `scripts/changerail_review_verdict.py validate --json` получает
  verdict с unknown fields, invalid date-time formats, wrong nested types или
  malformed nested reviewer/acceptance/finding data
- **THEN** helper завершается non-zero со structured diagnostic и не сообщает,
  что verdict valid

#### Scenario: Publish freshness проверяет malformed go verdict
- **WHEN** publish валидирует malformed `go` verdict с `--check-fresh`
- **THEN** validation завершается fail до того, как freshness может разрешить
  staging

### Requirement: Contract schema validation общая для helpers и tests
Helper smoke tests для manifest и verdict validation MUST проверять тот же
schema-backed validation path, который используют CLI helpers, или включать
negative fixtures, которые падают при drift helper validation от tracked schemas.

#### Scenario: Negative fixture нарушает additionalProperties
- **WHEN** smoke fixture добавляет unknown nested field, запрещенный schema
- **THEN** соответствующий helper завершается non-zero

#### Scenario: Negative fixture нарушает date-time format
- **WHEN** smoke fixture использует non-date-time value в schema `format` field
- **THEN** соответствующий helper завершается non-zero

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

### Requirement: Release checks покрывают все contract schemas
ChangeRail release и verification documentation MUST описывать полный публичный
contract schema set: review verdict, review cycle history, delivery manifest,
delivery run и evidence index.

#### Scenario: Maintainer проверяет release checks
- **WHEN** maintainer читает release или contract documentation
- **THEN** documented schema coverage включает все пять публичных
  `changerail-*.schema.json` contract files

### Requirement: Release schema validation gate
ChangeRail release verification MUST validate every public contract schema with
Draft 2020-12 meta-schema checks and fixture-backed document validation.

#### Scenario: Public schema is malformed
- **WHEN** a tracked `schemas/changerail-*.schema.json` file is not a valid
  Draft 2020-12 schema
- **THEN** the release schema validation smoke exits non-zero

#### Scenario: Helper and schema drift apart
- **WHEN** a positive or negative fixture no longer matches the helper-backed
  validation contract for review verdict, review cycle history, delivery
  manifest, delivery run or evidence index
- **THEN** the release schema validation smoke exits non-zero
