# changerail-repository-knowledge Specification

## Purpose
Зафиксировать opt-in repository knowledge catalog и maintenance policy
contracts, validation semantics и deterministic generated index behavior для
future ChangeRail maintenance harness.

## Requirements
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

### Requirement: Repository maintenance CLI validation
ChangeRail MUST provide shared-runtime POSIX and native Windows helper
entrypoints for repository knowledge catalog validation.

#### Scenario: Maintainer validates default catalog and policy
- **WHEN** `bin/changerail-maintenance validate-catalog` runs without path overrides
- **THEN** the helper validates `.changerail/knowledge.yaml` and `.changerail/maintenance.yaml`
- **AND** exits zero only when schema and semantic validation pass

#### Scenario: Maintainer validates overridden paths
- **WHEN** `bin/changerail-maintenance validate-catalog --catalog <path> --policy <path>` runs
- **THEN** the helper validates the supplied repository-relative files
- **AND** rejects absolute or traversal override paths fail-closed

#### Scenario: Native Windows wrapper is available
- **WHEN** a native Windows operator invokes `bin\\changerail-maintenance.cmd`
- **THEN** the wrapper delegates to the same shared Python runtime command surface

### Requirement: Repository knowledge generated index
ChangeRail MUST render a deterministic repository knowledge index from validated
catalog and policy input, and MUST keep default and check mode read-only.

#### Scenario: Check mode observes no drift
- **WHEN** `bin/changerail-maintenance render-index --check` renders the expected index
- **AND** the configured generated index file already matches
- **THEN** the helper exits zero without modifying tracked files

#### Scenario: Check mode reports drift
- **WHEN** `bin/changerail-maintenance render-index --check` renders content that differs from the configured generated index file
- **THEN** the helper exits non-zero
- **AND** reports the configured generated index path
- **AND** does not modify the file

#### Scenario: Write mode updates only generated index
- **WHEN** `bin/changerail-maintenance render-index --write` runs
- **THEN** the helper writes only the configured generated index path
- **AND** repeated `--write` runs are idempotent

### Requirement: Repository knowledge index ordering
Repository knowledge index rendering MUST produce stable ordering independent of
YAML record order.

#### Scenario: Catalog order changes
- **WHEN** two valid catalogs contain the same records in different YAML order
- **THEN** rendered index content is identical

#### Scenario: Index lists catalog classifications
- **WHEN** the index is rendered
- **THEN** each catalog record appears with its path, status, type, owner and review metadata

### Requirement: Repository knowledge dogfood catalog
ChangeRail MUST include a minimal public-safe dogfood catalog for its canonical
docs and a generated index that can be checked by the maintenance CLI.

#### Scenario: Dogfood catalog validates
- **WHEN** `bin/changerail-maintenance validate-catalog` runs in the ChangeRail repository
- **THEN** the dogfood catalog and policy validate successfully

#### Scenario: Dogfood index is current
- **WHEN** `bin/changerail-maintenance render-index --check` runs in the ChangeRail repository
- **THEN** the generated dogfood index is current

### Requirement: Repository maintenance scan policy
ChangeRail MUST allow `changerail.maintenance-policy.v1` documents to declare
optional maintenance scan configuration without invalidating the minimal policy
published by the repository knowledge contract.

#### Scenario: Minimal policy remains valid
- **WHEN** a policy contains only `schema`, `catalog_path` and `generated_index_path`
- **THEN** repository knowledge validation accepts the policy
- **AND** no scan detectors are implied as enabled by that minimal policy

#### Scenario: Scan policy declares detector scope
- **WHEN** a policy declares scan include globs, exclude globs, enabled detectors,
  severity threshold, timeout and per-detector options
- **THEN** validation accepts the fields as optional additive configuration
- **AND** rejects unknown contract-owned scan fields
- **AND** rejects absolute paths, traversal paths and root escapes in path-like
  scan fields

### Requirement: Repository maintenance scan command
ChangeRail MUST provide a read-only `bin/changerail-maintenance scan` command
that runs without LLM involvement and emits one schema-bound JSON report.

#### Scenario: Scan completes below threshold
- **WHEN** `bin/changerail-maintenance scan --json` can load valid catalog and
  policy configuration and no finding reaches the configured fail threshold
- **THEN** the command exits `0`
- **AND** stdout contains exactly one `changerail.maintenance-scan-report.v1`
  JSON document
- **AND** the repository working tree content is not modified

#### Scenario: Scan finds configured threshold violation
- **WHEN** scan generates a complete schema-valid report with at least one
  finding at or above the configured `--fail-on` threshold
- **THEN** the command exits `1`
- **AND** stdout still contains exactly one machine-readable report document

#### Scenario: Scan cannot create a valid report
- **WHEN** scan receives invalid configuration or cannot create a schema-valid
  report
- **THEN** the command exits `2`
- **AND** stdout contains one machine-readable diagnostic document rather than
  mixed human output

### Requirement: Catalog coverage detector
The maintenance scan MUST check catalog coverage only against the explicitly
configured documentation universe.

#### Scenario: Document in configured universe is uncovered
- **WHEN** scan discovers a knowledge file through configured include/exclude
  globs and no active catalog record covers that file
- **THEN** the coverage detector reports an actionable finding naming the
  repository-relative path

#### Scenario: Empty configured universe is not silent green
- **WHEN** the configured documentation universe matches no files
- **THEN** scan records a detector finding or detector error for empty coverage
  input
- **AND** the report does not treat absence of discovered files as a silent pass

### Requirement: Repository knowledge orphan detector
The maintenance scan MUST distinguish missing catalog targets from discovered
knowledge files that are not covered by an active catalog record.

#### Scenario: Active catalog target is missing
- **WHEN** an active catalog record references a path that does not exist
- **THEN** scan reports a missing-target finding for that catalog record

#### Scenario: Discovered knowledge file is orphaned
- **WHEN** a file in the configured documentation universe exists but is not
  covered by any active catalog record
- **THEN** scan reports an orphan-discovered-file finding for that file

### Requirement: Markdown local link and anchor detector
The maintenance scan MUST validate local Markdown links and anchors using a
maintained Markdown parser and a documented GitHub-compatible anchor algorithm.

#### Scenario: Local link target is missing
- **WHEN** a Markdown file in the configured active knowledge scope links to a
  missing repository-relative target
- **THEN** scan reports a link finding with source path, link target and
  normalized repository-relative evidence

#### Scenario: Heading anchor is stale
- **WHEN** a Markdown link points to an anchor that is not produced by the
  documented heading anchor algorithm, including duplicate heading suffixes
- **THEN** scan reports an anchor finding for the source path and target
  fragment

### Requirement: Generated knowledge freshness detector
The maintenance scan MUST check generated knowledge freshness passively through
maintained source/output fingerprints or the existing deterministic
`render-index --check` behavior.

#### Scenario: Generated index is stale
- **WHEN** configured catalog and policy input would render a different
  generated index than the tracked output
- **THEN** scan reports a stale-generated-output finding
- **AND** does not rewrite the generated file

#### Scenario: Arbitrary generator is configured
- **WHEN** policy attempts to require an arbitrary generator command for scan
  freshness
- **THEN** scan rejects or ignores the command fail-closed
- **AND** does not execute the arbitrary command implicitly

### Requirement: Forbidden active reference detector
The maintenance scan MUST check forbidden active references only inside the
configured active knowledge scope and report actionable relative-path evidence.

#### Scenario: Forbidden reference appears in active scope
- **WHEN** a configured forbidden reference pattern is present in an active
  knowledge file
- **THEN** scan reports a finding naming the source path and matching policy id

#### Scenario: Forbidden reference appears outside active scope
- **WHEN** a configured forbidden reference pattern appears only outside the
  configured active knowledge scope
- **THEN** scan does not report it as an active-reference violation

### Requirement: Maintenance adapter policy configuration
ChangeRail maintenance policy MUST allow optional adapter detector configuration
without adding language-specific analyzer dependencies to ChangeRail core.

#### Scenario: Adapter policy declares argv
- **WHEN** policy configures an adapter with id, argv array, timeout and
  detector options
- **THEN** policy validation accepts the adapter configuration
- **AND** rejects shell-string command configuration for adapter execution

#### Scenario: Minimal policy omits adapters
- **WHEN** a policy omits adapter configuration
- **THEN** existing catalog validation, index rendering and core scan behavior
  remain unaffected

### Requirement: Maintenance adapter execution boundary
The maintenance scan MUST execute configured adapters without a shell, from the
repository root, with a bounded timeout.

#### Scenario: Adapter exits successfully
- **WHEN** a configured adapter process exits zero with schema-valid JSON output
- **THEN** scan maps its findings into the maintenance scan report
- **AND** preserves repository-relative evidence paths after safe-path
  normalization

#### Scenario: Adapter times out
- **WHEN** a configured adapter exceeds its timeout
- **THEN** scan records a detector-error result for that adapter
- **AND** does not interpret the adapter as a green architecture result

### Requirement: Maintenance adapter failure handling
Adapter failure, invalid output or unsafe evidence MUST fail closed as detector
errors rather than successful detector results.

#### Scenario: Adapter exits non-zero
- **WHEN** a configured adapter exits with a non-zero status
- **THEN** scan records a detector-error result with the adapter id and failure
  class

#### Scenario: Adapter emits invalid JSON
- **WHEN** a configured adapter emits output that is not a schema-valid adapter
  result document
- **THEN** scan records a detector-error result
- **AND** the report does not treat the adapter as passing

#### Scenario: Adapter emits path escape
- **WHEN** an adapter finding includes an absolute path, traversal path or
  repository root escape
- **THEN** scan records a detector-error result for unsafe adapter output
- **AND** does not include the unsafe path as trusted finding evidence
