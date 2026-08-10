## ADDED Requirements

### Requirement: Instruction-budget-aware templates
Project templates MUST render one explicit instruction budget source of truth
and MUST keep project-specific rules before generated shared methodology so
budget remediation can distinguish the two ownership classes.

#### Scenario: Default template is measured
- **WHEN** bootstrap smoke renders `AGENTS.md`
- **THEN** the UTF-8 byte size is measured against the tracked Codex budget
- **AND** the fixture fails if default content reaches the 85 percent warning
  threshold

#### Scenario: Project rules approach the budget
- **WHEN** a fixture expands project-specific instructions past 85 percent but
  not beyond the budget
- **THEN** verification emits a non-blocking warning naming both measured and
  allowed bytes

### Requirement: Runtime evidence guidance is public-safe
Templates MUST state that raw Codex diagnostic output remains ignored and that
only allowlisted redacted fields may appear in reports, cards or documentation.

#### Scenario: Runtime guidance is scanned
- **WHEN** public-surface checks inspect generated guidance
- **THEN** it contains no example credential, private home path or raw doctor
  output
