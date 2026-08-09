## ADDED Requirements

### Requirement: Maintenance feedback command
ChangeRail MUST provide a read-only `bin/changerail-maintenance feedback`
command that validates explicit feedback input records and emits exactly one
`changerail.maintenance-detector-result.v1` JSON document for a declared
adapter id.

#### Scenario: Feedback emits adapter detector result
- **WHEN** `bin/changerail-maintenance feedback --adapter-id lifecycle --review-history <path> --json` receives a schema-valid review-cycle history record
- **THEN** stdout contains exactly one `changerail.maintenance-detector-result.v1` document
- **AND** the detector result id is `adapter-lifecycle`
- **AND** the command does not modify tracked files, ignored runtime files or external systems

#### Scenario: Mixed invalid input fails closed
- **WHEN** feedback receives one valid record and one malformed, unsafe or schema-invalid record
- **THEN** the output detector result contains detector errors describing the invalid record
- **AND** the result status is `error`
- **AND** the command does not silently discard the invalid record while claiming a complete pass

### Requirement: Review history feedback normalization
Maintenance feedback MUST normalize schema-valid `changerail.review-cycle-history.v1`
review finding details into maintenance detector findings without copying review
detail prose or raw file content.

#### Scenario: Review finding preserves identity metadata
- **WHEN** feedback normalizes a review-cycle history finding detail
- **THEN** the resulting detector finding preserves the source record reference, review cycle, original finding id and severity
- **AND** safe affected repository-relative paths are preserved as finding subjects
- **AND** stable subject identity includes the original finding id so unrelated review findings do not collapse onto one fingerprint

#### Scenario: Review prose is not copied
- **WHEN** a review finding detail contains summary or detail prose
- **THEN** feedback emits only a generic detector finding message and scalar source metadata
- **AND** it does not copy the review summary, detail prose or raw file content into normalized evidence

#### Scenario: Unsafe review path fails closed
- **WHEN** a review finding detail contains an absolute path, traversal path or repository root escape
- **THEN** feedback emits an `unsupported_review_history` detector error
- **AND** the unsafe path is not copied into the detector finding output

### Requirement: Blocked delivery-run feedback normalization
Maintenance feedback MUST normalize only schema-valid delivery-run records that
represent structured blocked terminal outcomes.

#### Scenario: Structured blocked run creates finding
- **WHEN** feedback receives a `changerail.delivery-run.v1` record whose `result` and `terminal_outcome` are `BLOCKED` and whose `terminal_reason` is present
- **THEN** feedback emits a detector finding with the source record reference, card id, terminal reason and retained evidence path metadata when present
- **AND** it does not parse logs, stderr, stdout or human diagnostics for finding text

#### Scenario: Legacy prose-only blocker is unsupported
- **WHEN** feedback receives a blocked delivery-run record with no structured `terminal_reason`
- **THEN** feedback emits an `unsupported_delivery_run` detector error
- **AND** it does not infer a maintenance finding from prose logs or diagnostics

#### Scenario: Non-blocked run does not create finding
- **WHEN** feedback receives a schema-valid delivery-run record that is not a blocked terminal outcome
- **THEN** feedback does not create a blocked-run finding for that record

### Requirement: External feedback producer boundary
Maintenance feedback MUST accept external feedback only through schema-valid
`changerail.maintenance-detector-result.v1` producer records and MUST apply the
same safe-path validation used by scan adapters.

#### Scenario: External producer result is merged
- **WHEN** feedback receives a schema-valid detector-result input path
- **THEN** its findings and detector errors are merged into the command output
- **AND** repository-relative evidence paths remain normalized

#### Scenario: Unsafe external producer output fails closed
- **WHEN** an external detector-result input contains unsafe finding paths
- **THEN** feedback emits an `unsafe_feedback_path` detector error
- **AND** it does not include the unsafe path as trusted finding evidence
