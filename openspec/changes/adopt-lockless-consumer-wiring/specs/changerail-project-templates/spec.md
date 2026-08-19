## ADDED Requirements

### Requirement: Consumer adoption migration guidance
Consumer adoption guidance MUST document the explicit lockless migration flow,
dry-run review, verification command and rollback boundary using only
public-safe generic examples.

#### Scenario: Operator reads lockless migration guidance
- **WHEN** an operator opens the consumer adoption runbook
- **THEN** it describes the difference between lockless compatibility,
  lockless adoption and lock-owned refresh
- **AND** it shows a generic dry-run command before the apply command
- **AND** it states that normal `--refresh-wiring` remains fail-closed without a
  consumer lock

#### Scenario: Rollback guidance is documented
- **WHEN** adoption fails or an operator decides not to keep the migration
- **THEN** the runbook identifies which tracked files may have been created by
  adoption
- **AND** it states that project-owned instructions, config, auth, source,
  board cards and unrelated Git state are outside migration scope

#### Scenario: Guidance stays public-safe
- **WHEN** migration docs and generated guidance are scanned before commit
- **THEN** examples use generic paths such as `/opt/changerail` and
  `/opt/example-project`
- **AND** they contain no private consumer names, raw field-validation logs,
  credentials or machine-local runtime reports
