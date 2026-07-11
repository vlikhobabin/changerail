## ADDED Requirements

### Requirement: Project-declared verification floor
OPSX delivery MUST execute every mandatory verification command declared by the
project rules, OpenSpec artifacts and affected toolchain, and MUST NOT treat
undeclared generic formatter, strict typing or environment matrices as
mandatory for every consumer project.

#### Scenario: Project declares required checks
- **WHEN** `AGENTS.md`, `openspec/config.yaml`, `tasks.md`, `design.md` or the
  changed toolchain declares a required command
- **THEN** delivery runs that command or stops with a recorded blocker

#### Scenario: Generic workflow has no universal formatter
- **WHEN** a consumer project does not declare a formatter or strict type check
  for the changed surface
- **THEN** OPSX does not require that command solely because the generic
  workflow is being used

### Requirement: Verification evidence claims
OPSX verification claims MUST identify the executed command, observed outcome
and retained evidence path when raw output is retained.

#### Scenario: Delivery records a passing check
- **WHEN** delivery records a verification command in the card, tasks or
  manifest
- **THEN** the record includes the command and a concrete outcome summary

### Requirement: Test adequacy evidence
OPSX delivery MUST explain whether added or changed tests can fail for the
claimed regression and observe the intended behavior source.

#### Scenario: Behavioral test is changed
- **WHEN** delivery adds or modifies a test for a behavioral claim
- **THEN** the evidence records why that test would fail if the behavior were
  broken

#### Scenario: RED evidence is not applicable
- **WHEN** a change is docs-only, config-only or otherwise not usefully
  test-first
- **THEN** delivery records why RED evidence is not applicable instead of
  claiming an unrun failure
