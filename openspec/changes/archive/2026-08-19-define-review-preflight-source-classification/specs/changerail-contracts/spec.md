## ADDED Requirements

### Requirement: Review preflight source classification
The deterministic review preflight MUST support an optional tracked
`.changerail/source-classification.yaml` consumer file using schema id
`changerail.source-classification.v1`. When present, the file MUST declare
repository-relative production source roots and source-kind rules using safe
paths that are neither absolute nor path-traversing. Missing classification
MUST preserve existing built-in source suffix behavior. Malformed
classification MUST block preflight before LLM review and MUST NOT be ignored
as a legacy fallback.

#### Scenario: Consumer declares production source kind
- **WHEN** preflight runs in a consumer repository with a schema-valid source
  classification file that declares a production root and source kind
- **THEN** files under that root matching the declared source kind are eligible
  for production complexity accounting
- **AND** built-in non-production path parts continue to exclude tests,
  fixtures, examples, schemas, templates, docs and OpenSpec artifacts

#### Scenario: Source classification is missing
- **WHEN** preflight runs without `.changerail/source-classification.yaml`
- **THEN** existing built-in production suffixes and executable helper rules
  continue to determine `added_production_loc`
- **AND** domain-specific suffixes that require declaration are not counted by
  default

#### Scenario: Source classification is unsafe
- **WHEN** the classification file contains an absolute path, traversal, root
  escape, duplicate source-kind id or schema-invalid value
- **THEN** preflight returns `blocked`
- **AND** the result includes a failing deterministic check explaining the
  invalid classification

### Requirement: Review preflight reports source-kind complexity detail
The `changerail.review-preflight-result.v1` result MUST retain aggregate
complexity guard fields and MUST include bounded source-kind detail for counted
production source. Each detail entry MUST identify the source kind, measure
strategy, counted path count, raw added lines and effective complexity
contribution without copying source content.

#### Scenario: Payload has mixed source kinds
- **WHEN** a scoped payload contains production files counted by more than one
  source kind
- **THEN** the preflight result reports the aggregate guard value
- **AND** it reports source-kind breakdown entries that explain how each kind
  contributed to the aggregate

#### Scenario: Breakdown remains public-safe
- **WHEN** preflight emits source-kind detail
- **THEN** the result contains repository-relative paths or counts only
- **AND** it does not include raw source snippets, customer data or ignored
  runtime content
