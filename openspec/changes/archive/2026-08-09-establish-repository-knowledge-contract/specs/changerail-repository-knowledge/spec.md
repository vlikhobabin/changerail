## ADDED Requirements

### Requirement: Repository knowledge default contract paths
ChangeRail MUST define the default tracked repository knowledge catalog path as
`.changerail/knowledge.yaml` and the default tracked maintenance policy path as
`.changerail/maintenance.yaml`.

#### Scenario: Maintainer uses default paths
- **WHEN** a maintainer validates repository knowledge without explicit path overrides
- **THEN** ChangeRail uses `.changerail/knowledge.yaml` as the catalog path
- **AND** uses `.changerail/maintenance.yaml` as the policy path

#### Scenario: Consumer has not opted in
- **WHEN** a repository has no `.changerail/maintenance.yaml`
- **THEN** existing ChangeRail delivery, review, publish and bootstrap behavior remains unaffected

### Requirement: Repository knowledge catalog schema
ChangeRail MUST publish a JSON Schema Draft 2020-12 catalog contract with schema
id `changerail.repository-knowledge.v1` and MUST reject contract-owned unknown
fields.

#### Scenario: Catalog record contains required fields
- **WHEN** a catalog record is validated
- **THEN** the record contains `path`, `status`, `type`, `owner`, `source_globs`, `verify`, `review_after` and `supersedes`
- **AND** schema validation fails when contract-owned objects contain unknown fields

#### Scenario: Catalog field null and empty semantics are validated
- **WHEN** optional record fields are empty
- **THEN** `source_globs`, `verify` and `supersedes` use empty arrays for no entries
- **AND** `owner` and `review_after` use `null` when no owner or review deadline is declared

### Requirement: Repository knowledge classifications
Catalog validation MUST support `status` values `active`, `historical`,
`superseded` and `generated`, and MUST support `type` values `tutorial`,
`how-to`, `reference`, `explanation`, `architecture`, `adr`, `runbook`,
`historical` and `generated` without requiring a specific directory layout.

#### Scenario: Supported status and type are accepted
- **WHEN** a catalog record uses a supported `status` and `type`
- **THEN** validation accepts the classification without checking directory names

#### Scenario: Active path must exist
- **WHEN** a catalog record has `status: active`
- **THEN** validation fails if the referenced `path` does not exist in the repository

#### Scenario: Superseded record declares replacement semantics
- **WHEN** a catalog record has `status: superseded`
- **THEN** validation accepts an empty `supersedes` list only as "no source replacement recorded"
- **AND** preserves any listed repository-relative replacement or predecessor paths

### Requirement: Repository knowledge safe paths
Repository knowledge validation MUST normalize repository-relative paths and
MUST reject absolute paths, traversal paths and paths that escape the repository
root.

#### Scenario: Absolute path is rejected
- **WHEN** catalog or policy YAML contains an absolute path
- **THEN** validation fails with a structured diagnostic for that field

#### Scenario: Traversal path is rejected
- **WHEN** catalog or policy YAML contains `..` traversal that would escape the repository root
- **THEN** validation fails with a structured diagnostic for that field

### Requirement: Maintenance policy schema
ChangeRail MUST publish a JSON Schema Draft 2020-12 maintenance policy contract
with schema id `changerail.maintenance-policy.v1` and MUST reject
contract-owned unknown fields.

#### Scenario: Policy declares generated index path
- **WHEN** maintenance policy YAML is validated
- **THEN** it can declare a repository-relative generated index path
- **AND** schema validation fails when contract-owned objects contain unknown fields

#### Scenario: Missing policy is explicit no-op
- **WHEN** the maintenance policy file is absent
- **THEN** validation reports the policy as not configured instead of mutating repository state

### Requirement: Repository knowledge YAML validation
ChangeRail MUST parse repository knowledge YAML with PyYAML and validate parsed
documents with JSON Schema Draft 2020-12 before applying semantic path checks.

#### Scenario: Invalid YAML fails before schema validation
- **WHEN** a catalog or policy file is not valid YAML
- **THEN** validation fails with a structured parse diagnostic

#### Scenario: Unknown field fixture fails
- **WHEN** a fixture contains a contract-owned unknown field
- **THEN** schema validation fails before the document is accepted

### Requirement: Repository knowledge public fixtures
ChangeRail MUST include public-safe valid and invalid fixtures for catalog and
policy validation, including path traversal and unknown-field negative cases.

#### Scenario: Valid fixture passes
- **WHEN** the repository knowledge smoke test validates the valid fixture set
- **THEN** catalog and policy validation exits zero

#### Scenario: Negative fixtures fail
- **WHEN** the repository knowledge smoke test validates invalid traversal or unknown-field fixtures
- **THEN** validation exits non-zero and reports the expected diagnostic class
