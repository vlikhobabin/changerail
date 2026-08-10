## ADDED Requirements

### Requirement: Consumer maintenance starter knowledge contract
ChangeRail MUST define the maintenance starter catalog/index contract for
bootstrapped consumers that explicitly opt in to maintenance.

#### Scenario: Starter catalog documents maintenance-owned files
- **WHEN** a generated consumer opts in to maintenance
- **THEN** the starter catalog treats `.changerail/knowledge.yaml` and `.changerail/maintenance.yaml` as first-class active knowledge records
- **AND** the records are validated by the same repository-relative safe-path rules as any consumer-owned record

#### Scenario: Starter catalog avoids exhaustive taxonomy
- **WHEN** a generated consumer receives starter records
- **THEN** records are limited to the generic ChangeRail maintenance and board skeleton files required for a green first scan
- **AND** ChangeRail does not impose domain-specific documentation categories or ownership rules on the consumer repository

### Requirement: First-run maintenance scan is deterministic and read-only
The first maintenance scan for a generated opted-in consumer MUST be
deterministic, read-only and below the configured failure threshold.

#### Scenario: First scan is below threshold
- **WHEN** `./bin/changerail-maintenance scan --json` runs in a fresh generated maintenance consumer
- **THEN** stdout contains one complete schema-valid `changerail.maintenance-scan-report.v1` document
- **AND** no detector finding or error reaches the configured `fail_on` threshold
- **AND** tracked and ignored repository files are not modified by the scan

#### Scenario: Index check remains explicit
- **WHEN** an operator later edits the starter catalog or policy
- **THEN** `render-index --check` can report drift without mutating files
- **AND** `render-index --write` remains the explicit write surface for refreshing the generated index
