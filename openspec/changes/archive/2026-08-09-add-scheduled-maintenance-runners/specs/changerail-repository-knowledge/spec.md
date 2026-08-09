## ADDED Requirements

### Requirement: Maintenance runner command surface
ChangeRail MUST provide shared-runtime POSIX and native Windows helper
entrypoints for bounded repository maintenance runs.

#### Scenario: Maintainer runs scan mode
- **WHEN** `bin/changerail-maintenance-runner scan --json` runs from a
  repository with valid maintenance configuration
- **THEN** the runner executes deterministic maintenance scan/report work
- **AND** it writes a `changerail.maintenance-run.v1` status below ignored
  `.runtime/changerail/maintenance/runs/`
- **AND** it does not require Codex authentication

#### Scenario: Native Windows runner is available
- **WHEN** a native Windows operator invokes
  `bin\changerail-maintenance-runner.cmd`
- **THEN** the wrapper delegates to the same shared Python runtime command
  surface as the POSIX runner

### Requirement: Maintenance runner bounded execution
The maintenance runner MUST default to read-only, single-workspace,
non-overlapping execution with explicit timeout and optional agent-budget
diagnostics.

#### Scenario: Concurrent run is blocked
- **WHEN** a maintenance run lock already exists for the workspace
- **THEN** the runner exits non-zero with structured lock diagnostics
- **AND** it does not start another scan or agent process

#### Scenario: Child execution times out
- **WHEN** scan or triage child execution exceeds the configured timeout
- **THEN** the runner records timeout diagnostics in run status
- **AND** it terminates the child and reports a blocked or failed result

### Requirement: Maintenance runner triage mode
The maintenance runner MUST distinguish deterministic scan mode from optional
agent triage mode and MUST fail closed on invalid agent output.

#### Scenario: Triage mode receives valid annotations
- **WHEN** the runner executes optional triage and the child produces
  schema-valid `changerail.maintenance-triage.v1` annotations
- **THEN** the runner records annotation and preview references in run status
- **AND** the retained outputs remain below ignored maintenance runtime state

#### Scenario: Triage mode receives invalid child output
- **WHEN** the triage child exits zero but does not produce the required
  schema-valid annotations or preview references
- **THEN** the runner records invalid-output diagnostics
- **AND** it does not treat the run as successful by scraping human prose

### Requirement: Maintenance scheduler examples
ChangeRail MUST publish public-safe scheduler examples for recurring
maintenance audit that are read-only by default and scheduler-neutral in core
behavior.

#### Scenario: GitHub scheduled example is inspected
- **WHEN** a maintainer reads the GitHub Actions maintenance example
- **THEN** the workflow uses `contents: read`
- **AND** it uploads ignored report output as an artifact
- **AND** it documents default-branch and at-least-once scheduler behavior

#### Scenario: Local scheduler examples are inspected
- **WHEN** a maintainer reads systemd or Codex scheduled task examples
- **THEN** each example uses repository cwd, bounded timeout and no overlapping
  runs
- **AND** local checkout mode documents the risk of operating on an active
  worktree

#### Scenario: CI separation is documented
- **WHEN** a maintainer reads the CI maintenance example
- **THEN** read-only analysis is separate from any job that would need write
  permissions, API credentials, comments, pull requests or publication
