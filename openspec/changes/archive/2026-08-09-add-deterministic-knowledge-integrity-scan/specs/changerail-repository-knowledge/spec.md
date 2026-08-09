## ADDED Requirements

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
