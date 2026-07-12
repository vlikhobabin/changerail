## ADDED Requirements

### Requirement: Review skill writes independence evidence
`changerail-review` MUST instruct reviewers to include the required
independence attestation in the canonical review verdict.

#### Scenario: Fresh reviewer writes a verdict
- **WHEN** `changerail-review` produces a verdict
- **THEN** the verdict includes machine-readable independence attestation
- **AND** the skill output identifies the reviewer context as fresh or stops
  before writing a verdict
