## ADDED Requirements

### Requirement: Maintenance operations runbook
ChangeRail MUST publish a public Russian maintenance operations runbook for
consumer repositories that explains the complete manual and agent-facing
maintenance lifecycle.

#### Scenario: Operator follows adoption flow
- **WHEN** an operator reads the maintenance operations runbook
- **THEN** it covers new bootstrap and existing repository adoption prerequisites
- **AND** it shows catalog, policy, generated index and first scan commands using generic public-safe paths
- **AND** it explains how to verify a green initial maintenance scan without reading implementation fixtures

#### Scenario: Runbook separates read-only and write operations
- **WHEN** an operator reads maintenance command examples
- **THEN** default read-only operations are separated from explicit writes such as `render-index --write`, `--write-state`, baseline write and card write
- **AND** no maintenance command is described as permission to commit, push, comment, open pull requests or mutate external systems

#### Scenario: Runbook covers feedback and quality
- **WHEN** an operator reads feedback and quality sections
- **THEN** review-cycle history, blocked delivery-run and external detector-result feedback inputs are documented
- **AND** text, JSON and CSV quality outputs are documented with `known` and `unknown` metric semantics

### Requirement: Maintenance scheduler examples are indexed
ChangeRail MUST index public maintenance scheduler examples from the main
documentation flow and document their safe prerequisites.

#### Scenario: Scheduler examples are discoverable
- **WHEN** an operator reads README, adoption docs or the maintenance runbook
- **THEN** the GitHub Actions, separated CI, Codex scheduled task and systemd examples are listed with their intended use
- **AND** each example points to prerequisites for consumer checkout and ChangeRail helper wiring

#### Scenario: Scheduler examples remain least privilege
- **WHEN** scheduler examples are described
- **THEN** read-only scheduled audit is the default
- **AND** any write-capable follow-up is described as a separate explicit workflow requiring separate authority
