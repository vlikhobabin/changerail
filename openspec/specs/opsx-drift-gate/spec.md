# opsx-drift-gate Specification

## Purpose
Зафиксировать workspace-level drift gate для OPSX consumer projects:
configured inventory, include/exclude policy, stable consumer classes,
machine-readable JSON output and fail-closed exit behavior.

## Requirements
### Requirement: Workspace drift gate
OPSX MUST provide `scripts/smoke-drift.py` as a workspace-level red/green gate
for configured consumer projects.

#### Scenario: Drift gate checks configured projects
- **WHEN** `python3 scripts/smoke-drift.py --config <path>` runs with a config
  that names workspace roots or explicit projects
- **THEN** it classifies each discovered non-excluded project and exits `0`
  only when every non-excluded project is connected to OPSX source

#### Scenario: Drift gate refuses missing inventory
- **WHEN** `python3 scripts/smoke-drift.py` runs without config, workspace root
  or explicit project input
- **THEN** it exits non-zero and reports that no drift inventory was provided

### Requirement: Drift inventory inputs
The drift gate MUST support operator-provided include/exclude inventory without
requiring tracked machine-local project lists.

#### Scenario: Explicit projects are included
- **WHEN** config or CLI input names `/opt/example-a` as a project
- **THEN** the report includes `/opt/example-a` even if no workspace root scan
  would discover it

#### Scenario: Workspace roots are scanned shallowly
- **WHEN** config or CLI input names `/opt/example-workspace` as a workspace
  root
- **THEN** only immediate child directories are considered candidate projects

#### Scenario: Excluded project is reported but not verified
- **WHEN** config or CLI input excludes `/opt/example-b`
- **THEN** the report classifies it as `explicitly_excluded` with the recorded
  reason when provided
- **AND** the exclusion does not make the gate fail

### Requirement: Consumer classification
The drift gate MUST classify consumers into stable machine-readable classes.

#### Scenario: OPSX source project passes
- **WHEN** a non-excluded project passes `bin/verify-project`
- **THEN** the project class is `opsx_source`

#### Scenario: Legacy source project is detected
- **WHEN** a non-excluded project fails `bin/verify-project` but its configured
  agent/helper symlink-и resolve under a configured legacy source root
- **THEN** the project class is `legacy_source`
- **AND** the gate exits non-zero

#### Scenario: Broken wiring project fails
- **WHEN** a non-excluded project has OPSX-like files but does not pass
  `bin/verify-project` and is not classified as legacy source
- **THEN** the project class is `broken_wiring`
- **AND** the gate exits non-zero

#### Scenario: Disconnected project fails
- **WHEN** a non-excluded project does not expose OPSX-like files or valid OPSX
  wiring
- **THEN** the project class is `disconnected`
- **AND** the gate exits non-zero

### Requirement: Drift report contract
The drift gate MUST emit machine-readable JSON with the canonical schema id
`opsx.drift-gate.v1`.

#### Scenario: Report contains aggregate summary
- **WHEN** the drift gate runs
- **THEN** it writes a JSON report under ignored runtime space by default
- **AND** the report records `schema`, `run_id`, `opsx_root`, `config_source`,
  `summary` and `projects[]`

#### Scenario: Project entry records classification evidence
- **WHEN** a project is classified
- **THEN** its report entry records `path`, `name`, `class`, `status`,
  `message`, `excluded`, `exclude_reason`, `verify_summary` and `indicators`

### Requirement: Public-safe drift artifacts
OPSX drift gate artifacts committed to the repository MUST avoid private
workspace names, customer data, secrets, runtime reports and machine-local
inventory.

#### Scenario: Drift gate examples remain generic
- **WHEN** docs, specs, cards or scripts describe drift-gate usage
- **THEN** they use generic examples such as `/opt/example-project`,
  `/opt/example-a` and `/opt/example-b`
- **AND** real inventory is expected under ignored operator paths such as
  `internal/`
