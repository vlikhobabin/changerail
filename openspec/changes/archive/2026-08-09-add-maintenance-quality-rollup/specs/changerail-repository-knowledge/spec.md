## ADDED Requirements

### Requirement: Maintenance quality rollup command
ChangeRail MUST provide a read-only `bin/changerail-maintenance quality`
command that reads explicit schema-valid maintenance lifecycle evidence and
emits human-readable, JSON and stable CSV quality views without changing
delivery metrics output.

#### Scenario: Quality rollup emits JSON
- **WHEN** `bin/changerail-maintenance quality --report <path> --json` receives a complete schema-valid lifecycle report
- **THEN** stdout contains exactly one `changerail.maintenance-quality-rollup.v1` JSON document
- **AND** the command does not modify tracked files, ignored runtime files or external systems

#### Scenario: Quality rollup emits stable CSV
- **WHEN** the operator requests CSV output
- **THEN** stdout is a sorted long-form table with columns `metric,value,unit,status`
- **AND** the command does not append fields to the existing delivery metrics CSV

#### Scenario: Text and JSON expose same metrics
- **WHEN** the operator requests text output instead of JSON
- **THEN** text output includes the same metric ids represented in JSON
- **AND** missing optional values are rendered as `unknown`

### Requirement: Maintenance quality rollup schema
ChangeRail MUST publish a JSON Schema Draft 2020-12 quality rollup contract with
schema id `changerail.maintenance-quality-rollup.v1`.

#### Scenario: Quality JSON validates
- **WHEN** quality rollup JSON is emitted
- **THEN** it validates against the tracked quality rollup schema
- **AND** schema validation rejects contract-owned unknown fields

#### Scenario: Metric status is explicit
- **WHEN** a quality metric cannot be calculated from supplied inputs
- **THEN** the metric contains `status: unknown`
- **AND** it does not report an inferred zero value

### Requirement: Maintenance proposal decision records
ChangeRail MUST publish a JSON Schema Draft 2020-12 proposal-decision contract
with schema id `changerail.maintenance-proposal-decision.v1` for ignored
runtime quality observations.

#### Scenario: Proposal decision record validates
- **WHEN** a proposal-decision record is supplied to quality rollup
- **THEN** it identifies proposal id, finding fingerprint, transformation class, accepted or rejected decision, decision timestamp and safe evidence references
- **AND** it validates against the tracked proposal-decision schema

#### Scenario: Proposal decision does not authorize fixes
- **WHEN** quality rollup reads accepted or rejected proposal decisions
- **THEN** it reports proposal decision counts only as quality observations
- **AND** it does not write cards, apply fixes, commit, push, comment, open PRs or mutate external systems

### Requirement: Maintenance quality metric semantics
Maintenance quality rollup MUST compute metrics only from complete schema-valid
inputs and MUST render insufficient optional evidence as `unknown`.

#### Scenario: Latest report supplies lifecycle counts
- **WHEN** the latest complete lifecycle report is available
- **THEN** quality rollup reports open, accepted and waived finding counts from that report

#### Scenario: Resolution requires complete ordered snapshots
- **WHEN** a finding exists in an earlier complete ordered snapshot and is absent from a later complete snapshot
- **THEN** quality rollup counts that finding as resolved

#### Scenario: Incomplete history renders resolution unknown
- **WHEN** report history is missing, unordered or includes incomplete snapshots
- **THEN** resolved finding count is `unknown`
- **AND** the rollup does not infer zero resolved findings

#### Scenario: Optional metrics remain unknown
- **WHEN** triage annotations, proposal decisions or instruction-budget producer records are not supplied
- **THEN** time-to-triage, proposal decision counts and instruction bytes are `unknown`

### Requirement: Maintenance quality catalog and board metrics
Maintenance quality rollup MUST calculate catalog and board metrics from
validated tracked repository state without mutating cards or catalog files.

#### Scenario: Catalog coverage uses validated catalog
- **WHEN** quality rollup reports catalog coverage
- **THEN** it uses the validated tracked catalog and configured knowledge scope
- **AND** invalid catalog or policy input fails closed instead of producing coverage metrics

#### Scenario: Board dedup metrics inspect origin markers
- **WHEN** lifecycle findings and board cards are available
- **THEN** quality rollup reports represented, missing and conflicting maintenance identities by inspecting exact `Maintenance Origin: <sha256 fingerprint>` markers
- **AND** it does not create or update board cards

#### Scenario: Stale generated findings use stable ids
- **WHEN** stale generated index or generated knowledge findings exist
- **THEN** quality rollup reports them from stable detector and rule ids
