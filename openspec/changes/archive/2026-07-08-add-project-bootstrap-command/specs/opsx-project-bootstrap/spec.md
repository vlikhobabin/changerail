## ADDED Requirements

### Requirement: Bootstrap project command
OPSX MUST provide `bin/bootstrap-project` to create a new generic consumer
project from tracked templates and OPSX source-of-truth symlink-и.

#### Scenario: Operator bootstraps a generic project
- **WHEN** an operator runs `bin/bootstrap-project /opt/example-project --name
  example-project --kind generic`
- **THEN** the target receives generated project files, OPSX symlink-и, helper
  wrappers and an OpenSpec skeleton

### Requirement: Refuse existing targets by default
Bootstrap MUST refuse to overwrite an existing non-empty target unless the
operator explicitly requests backup mode.

#### Scenario: Target already contains files
- **WHEN** bootstrap is run for a non-empty existing target without
  `--backup-existing`
- **THEN** bootstrap exits non-zero before changing the target

### Requirement: Dry-run mode
Bootstrap MUST support a dry-run mode that reports planned operations without
creating or modifying the target project.

#### Scenario: Operator previews bootstrap
- **WHEN** bootstrap is run with `--dry-run`
- **THEN** planned file, directory and symlink actions are printed and the
  target project is not created

### Requirement: Bootstrap verification handoff
Bootstrap MUST run `verify-project` after generating a project unless the
operator explicitly skips verification for diagnostics.

#### Scenario: Generated project is verified
- **WHEN** bootstrap completes project generation
- **THEN** it runs `bin/verify-project <target>` and fails if verification
  fails

### Requirement: Bootstrap smoke evidence
OPSX MUST provide smoke coverage that exercises bootstrap end-to-end under
ignored runtime space.

#### Scenario: Bootstrap smoke runs
- **WHEN** `python3 scripts/smoke-bootstrap-project.py` runs
- **THEN** it creates a temporary consumer under `.runtime`, verifies it and
  writes any report under ignored runtime space
