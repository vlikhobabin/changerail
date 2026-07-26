## ADDED Requirements

### Requirement: Delivery plan generation helper
The delivery runner MUST provide a non-live helper command that generates a
schema-backed queue plan from ordered card paths and optional dependency
declarations.

#### Scenario: Operator generates a serial plan
- **WHEN** an operator invokes `bin/changerail-delivery-runner generate-plan`
  with a plan id, workspace alias/path and ordered card paths
- **THEN** the command emits a `changerail.delivery-plan.v1` JSON plan whose
  cards preserve the input order
- **AND** no child delivery process is started

#### Scenario: Operator adds dependencies
- **WHEN** an operator supplies dependency declarations for generated card ids
- **THEN** the emitted plan records those dependencies under the matching card
  entries
- **AND** invalid dependency references fail before writing the plan

#### Scenario: Generated plan uses existing validation
- **WHEN** `generate-plan` emits or writes a plan
- **THEN** the payload validates against
  `schemas/changerail-delivery-plan.schema.json`
- **AND** the generated plan can be consumed by `plan` and `preflight-plan`
  without live child delivery
