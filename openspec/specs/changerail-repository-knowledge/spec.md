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

### Requirement: Maintenance lifecycle report contract
ChangeRail MUST publish a JSON Schema Draft 2020-12 lifecycle report contract
with schema id `changerail.maintenance-report.v1`. The report MUST be
normalized from a complete schema-valid `changerail.maintenance-scan-report.v1`
source and MUST contain run metadata, source scan metadata, detector summary
and normalized lifecycle findings.

#### Scenario: Complete scan normalizes to lifecycle report
- **WHEN** `bin/changerail-maintenance report --json` runs against valid
  repository knowledge maintenance configuration
- **THEN** stdout contains exactly one `changerail.maintenance-report.v1` JSON
  document
- **AND** every normalized finding contains `fingerprint`,
  `evidence_fingerprint`, `detector`, `rule`, `severity`, `confidence`, `path`,
  `evidence_refs`, `remediation`, `first_seen`, `owner`, `risk_class` and
  lifecycle `status`

#### Scenario: Invalid source scan is rejected
- **WHEN** lifecycle normalization receives an incomplete or schema-invalid
  `changerail.maintenance-scan-report.v1` source
- **THEN** the command exits non-zero
- **AND** the emitted lifecycle report is marked incomplete with a blocker
  diagnostic instead of silently accepting partial detector output

### Requirement: Maintenance finding identity
ChangeRail MUST compute each lifecycle finding identity from canonical JSON over
`identity_version`, detector result id, finding rule/code and normalized
repository-relative subject. The public fingerprint form MUST be
`sha256:<lowercase-hex>`.

#### Scenario: Volatile finding fields do not change identity
- **WHEN** a repeated scan observes the same detector, rule and normalized
  subject with a different message, severity, timestamp or workspace root
- **THEN** the lifecycle finding keeps the same `fingerprint`
- **AND** identity material does not include the volatile field values

#### Scenario: Subject change changes identity
- **WHEN** a repeated scan observes the same detector and rule for a different
  normalized repository-relative subject
- **THEN** the lifecycle finding has a different `fingerprint`

### Requirement: Maintenance evidence fingerprint
ChangeRail MUST compute `evidence_fingerprint` separately from finding identity
using canonical JSON over sanitized material evidence. Evidence, raw message
text and timestamps MUST NOT be copied into identity material.

#### Scenario: Evidence change preserves identity
- **WHEN** a repeated scan observes the same finding identity with changed
  material evidence
- **THEN** the lifecycle finding keeps the same `fingerprint`
- **AND** `evidence_fingerprint` changes

#### Scenario: Unsafe evidence fails closed
- **WHEN** detector evidence contains an absolute path, traversal path, unknown
  local path shape or secret-like raw value
- **THEN** lifecycle normalization rejects that evidence with a blocker
  diagnostic
- **AND** the unsafe value is not copied into lifecycle output

### Requirement: Maintenance runtime state continuity
ChangeRail MUST keep maintenance lifecycle runtime state atomically below
`.runtime/changerail/maintenance/state.json`. Lifecycle normalization MUST be
read-only by default, and durable state updates MUST require explicit
`--write-state`.

#### Scenario: State write is explicit and atomic
- **WHEN** `bin/changerail-maintenance report --json --write-state` completes
  successfully
- **THEN** `.runtime/changerail/maintenance/state.json` is written atomically
- **AND** repeated runs with the restored state preserve `first_seen` for the
  same finding identity

#### Scenario: Custom state path stays in runtime root
- **WHEN** `bin/changerail-maintenance report --json --write-state --state <path>`
  receives a custom state path outside `.runtime/changerail/maintenance/`
- **THEN** lifecycle normalization exits non-zero
- **AND** the custom path is not written

#### Scenario: Default report does not claim continuity
- **WHEN** `bin/changerail-maintenance report --json` runs without restored
  state and without `--write-state`
- **THEN** repository tracked files are not modified
- **AND** each finding `first_seen` is the current observation
- **AND** the report metadata states that cross-run continuity was not restored

#### Scenario: Corrupt state fails closed
- **WHEN** `.runtime/changerail/maintenance/state.json` is corrupt or has an
  unsupported schema version
- **THEN** lifecycle normalization exits non-zero
- **AND** the existing state file is not replaced implicitly

### Requirement: Maintenance baseline and waiver contract
ChangeRail MUST publish a JSON Schema Draft 2020-12 baseline contract for
`.changerail/maintenance-baseline.yaml` with separate `accepted` and `waivers`
collections. Acceptance MUST be keyed by lifecycle finding identity
fingerprint. Each waiver MUST include `owner`, `reason` and either an
ISO-8601 `expires_at` or `review_after` boundary.

#### Scenario: Baseline acceptance is schema backed
- **WHEN** `.changerail/maintenance-baseline.yaml` contains accepted finding
  identities
- **THEN** `bin/changerail-maintenance accept-baseline --write` writes only the
  baseline file
- **AND** the resulting file validates against the maintenance baseline schema

#### Scenario: Expired waiver does not suppress finding
- **WHEN** a lifecycle finding matches a waiver whose `expires_at` or
  `review_after` boundary is in the past
- **THEN** the lifecycle output keeps the finding open
- **AND** the expired waiver is reported as not suppressing the finding

#### Scenario: Active date-only waiver remains report-valid
- **WHEN** a lifecycle finding matches a waiver with a future date-only
  `expires_at` or `review_after` boundary
- **THEN** the lifecycle output marks the finding waived
- **AND** `suppressed_until` is normalized to a report-valid UTC date-time

### Requirement: Maintenance baseline preview defaults
ChangeRail maintenance baseline operations MUST be read-only by default and
MUST mutate tracked baseline content only when explicit `--write` is supplied.

#### Scenario: Accept baseline preview does not mutate files
- **WHEN** `bin/changerail-maintenance accept-baseline --json` runs without
  `--write`
- **THEN** it emits a schema-valid preview artifact or JSON summary
- **AND** the repository working tree content is not modified

#### Scenario: Accept baseline write is scoped
- **WHEN** `bin/changerail-maintenance accept-baseline --write` runs
- **THEN** the only tracked file it creates or updates is
  `.changerail/maintenance-baseline.yaml`

### Requirement: Maintenance triage annotations
ChangeRail MUST accept schema-bound maintenance triage annotations and MUST NOT
invoke an LLM as part of `triage` command execution.

#### Scenario: Triage validates supplied annotations
- **WHEN** `bin/changerail-maintenance triage --annotations <path> --json`
  receives valid annotation JSON
- **THEN** the command emits normalized schema-valid annotations
- **AND** no LLM or external model process is invoked

#### Scenario: Invalid triage fails closed
- **WHEN** supplied triage annotations violate the schema
- **THEN** the command exits non-zero
- **AND** it emits one machine-readable diagnostic document

### Requirement: Maintenance board card bridge
ChangeRail MUST provide a preview-first board-card bridge from lifecycle
findings to ChangeRail board cards. Written cards MUST carry exactly one
machine-readable line `Maintenance Origin: <sha256 fingerprint>`.

#### Scenario: Card bridge preview does not mutate board
- **WHEN** `bin/changerail-maintenance cards --json` runs without `--write`
- **THEN** preview artifacts are retained under ignored
  `.runtime/changerail/maintenance/`
- **AND** no tracked board card is created or updated

#### Scenario: Card bridge writes exact origin marker
- **WHEN** `bin/changerail-maintenance cards --write` creates a board card for
  a lifecycle finding
- **THEN** the tracked card contains exactly one line
  `Maintenance Origin: <sha256 fingerprint>`
- **AND** the card title, summary and evidence references contain only
  sanitized repository-relative metadata

#### Scenario: Card bridge rejects unsafe report material
- **WHEN** `bin/changerail-maintenance cards --write` receives a lifecycle
  report whose open finding contains an absolute path, unsafe local path shape,
  secret-like `finding.path` or other secret-like card material
- **THEN** the command exits non-zero
- **AND** no tracked board card is created or updated for that finding

#### Scenario: Card bridge deduplicates across board lanes
- **WHEN** a lifecycle finding has the same fingerprint as a card already
  present under `openspec/board/1.backlog`, `2.todo`, `3.inprogress`, `4.done`
  or `5.canceled`
- **THEN** `bin/changerail-maintenance cards --write` updates that existing
  card evidence summary
- **AND** it does not create another card for the same identity

### Requirement: Maintenance audit agent workflow
The repository knowledge maintenance workflow MUST support an agent-facing
read-only audit mode that consumes deterministic scan and lifecycle report
contracts without changing repository state.

#### Scenario: Audit runs deterministic commands
- **WHEN** an agent runs maintenance audit without a supplied report
- **THEN** it uses `bin/changerail-maintenance scan --json` and/or
  `bin/changerail-maintenance report --json` as deterministic inputs
- **AND** it does not pass state-write, baseline-write or card-write flags

#### Scenario: Audit consumes retained report
- **WHEN** an agent receives an existing schema-valid maintenance report path
- **THEN** it may explain findings and ambiguity in prose
- **AND** it treats unsupported or invalid report data as an audit finding
  instead of silently normalizing it outside the deterministic CLI

### Requirement: Maintenance triage agent workflow
The repository knowledge maintenance workflow MUST support bounded agent triage
that produces schema-valid annotations and card previews under ignored runtime
state before any tracked board mutation is requested.

#### Scenario: Triage writes ignored annotations
- **WHEN** maintenance triage records agent annotations
- **THEN** the annotations validate against `changerail.maintenance-triage.v1`
- **AND** the files are written below `.runtime/changerail/maintenance/`

#### Scenario: Triage previews cards before write
- **WHEN** maintenance triage prepares board-card output
- **THEN** it runs or consumes the preview-first card bridge without `--write`
- **AND** no tracked board card is created or updated unless the operator
  separately requested explicit card writes

### Requirement: Maintenance runner command surface
ChangeRail MUST provide shared-runtime POSIX and native Windows helper
entrypoints for bounded repository maintenance runs.

#### Scenario: Maintainer runs scan mode
- **WHEN** `bin/changerail-maintenance-runner scan --json` runs from a
  repository with valid maintenance configuration
- **THEN** the runner executes deterministic maintenance scan/report work
- **AND** it writes a `changerail.maintenance-run.v1` status below ignored
  `.runtime/changerail/maintenance/runs/`
- **AND** it does not require Codex authentication

#### Scenario: Native Windows runner is available
- **WHEN** a native Windows operator invokes
  `bin\changerail-maintenance-runner.cmd`
- **THEN** the wrapper delegates to the same shared Python runtime command
  surface as the POSIX runner

### Requirement: Maintenance runner bounded execution
The maintenance runner MUST default to read-only, single-workspace,
non-overlapping execution with explicit timeout and optional agent-budget
diagnostics.

#### Scenario: Concurrent run is blocked
- **WHEN** a maintenance run lock already exists for the workspace
- **THEN** the runner exits non-zero with structured lock diagnostics
- **AND** it does not start another scan or agent process

#### Scenario: Child execution times out
- **WHEN** scan or triage child execution exceeds the configured timeout
- **THEN** the runner records timeout diagnostics in run status
- **AND** it terminates the child and reports a blocked or failed result

### Requirement: Maintenance runner triage mode
The maintenance runner MUST distinguish deterministic scan mode from optional
agent triage mode and MUST fail closed on invalid agent output.

#### Scenario: Triage mode receives valid annotations
- **WHEN** the runner executes optional triage and the child produces
  schema-valid `changerail.maintenance-triage.v1` annotations
- **THEN** the runner records annotation and preview references in run status
- **AND** the retained outputs remain below ignored maintenance runtime state

#### Scenario: Triage mode receives invalid child output
- **WHEN** the triage child exits zero but does not produce the required
  schema-valid annotations or preview references
- **THEN** the runner records invalid-output diagnostics
- **AND** it does not treat the run as successful by scraping human prose

### Requirement: Maintenance scheduler examples
ChangeRail MUST publish public-safe scheduler examples for recurring
maintenance audit that are read-only by default and scheduler-neutral in core
behavior.

#### Scenario: GitHub scheduled example is inspected
- **WHEN** a maintainer reads the GitHub Actions maintenance example
- **THEN** the workflow uses `contents: read`
- **AND** it uploads ignored report output as an artifact
- **AND** it documents default-branch and at-least-once scheduler behavior

#### Scenario: Local scheduler examples are inspected
- **WHEN** a maintainer reads systemd or Codex scheduled task examples
- **THEN** each example uses repository cwd, bounded timeout and no overlapping
  runs
- **AND** local checkout mode documents the risk of operating on an active
  worktree

#### Scenario: CI separation is documented
- **WHEN** a maintainer reads the CI maintenance example
- **THEN** read-only analysis is separate from any job that would need write
  permissions, API credentials, comments, pull requests or publication
