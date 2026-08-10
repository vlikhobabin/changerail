## ADDED Requirements

### Requirement: Public-safe consumer CI template
The project template set MUST include an opt-in consumer CI workflow that uses
read-only repository permissions, exact lock-driven ChangeRail checkout and the
same verification commands documented for local consumers.

#### Scenario: CI template is rendered
- **WHEN** bootstrap renders the CI opt-in
- **THEN** `.github/workflows/changerail-consumer-verify.yml` is generated
- **AND** it reads the consumer lock rather than a floating branch

#### Scenario: Workflow authority is inspected
- **WHEN** a maintainer reviews the generated workflow
- **THEN** repository permission is read-only
- **AND** no commit, push, PR, publish or deployment step is present

#### Scenario: Workflow runs without Codex credentials
- **WHEN** baseline CI executes without Codex auth state
- **THEN** static consumer verification can complete
- **AND** no delivery runner is launched

### Requirement: Provider-neutral CI handoff
Generated guidance MUST identify the lock-driven checkout, repair and verify
sequence as the provider-neutral contract even when the initial tracked
template targets GitHub Actions.

#### Scenario: Operator uses another CI provider
- **WHEN** an operator reads generated CI guidance
- **THEN** exact source checkout, disposable wiring repair and verification
  commands are stated independently of GitHub-specific syntax
