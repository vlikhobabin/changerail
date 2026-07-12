## ADDED Requirements

### Requirement: Consumer board templates expose current workflow guidance
Project board templates MUST give generated consumers the current ChangeRail
card lifecycle and a canonical pointer to reusable workflow guidance.

#### Scenario: Consumer board README is generated
- **WHEN** `bin/bootstrap-project /opt/example-project` renders the project
  board README
- **THEN** the generated file describes the `1.backlog -> 2.todo ->
  3.inprogress -> 4.done` review-gated lifecycle
- **AND** it points maintainers to the canonical ChangeRail guide or shared
  methodology for the orchestrator, worker and independent reviewer model

#### Scenario: Template content is reviewed for public safety
- **WHEN** project templates are scanned before commit
- **THEN** workflow examples use generic ChangeRail paths such as
  `/opt/changerail` and `/opt/example-project`
