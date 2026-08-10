## ADDED Requirements

### Requirement: Maintenance contract reference inventory is complete
ChangeRail contract documentation MUST list every tracked public maintenance
schema and keep feedback, quality rollup and proposal-decision references
current.

#### Scenario: Maintainer inspects contract reference
- **WHEN** a maintainer reads `docs/changerail-contracts.md`
- **THEN** the schema inventory includes `changerail-maintenance-quality-rollup.schema.json`
- **AND** it includes `changerail-maintenance-proposal-decision.schema.json`
- **AND** it does not describe the implemented maintenance harness as only a future harness

#### Scenario: Feedback reference is current
- **WHEN** a maintainer reads the maintenance feedback reference
- **THEN** it documents review-history, blocked delivery-run and external detector-result inputs
- **AND** it states that invalid, unsafe or unsupported feedback inputs fail closed instead of being inferred from prose

#### Scenario: Quality reference is current
- **WHEN** a maintainer reads the quality-rollup reference
- **THEN** it documents text, JSON and CSV output modes
- **AND** it explains complete/incomplete evidence and `known`/`unknown` metric status semantics
