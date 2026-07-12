## MODIFIED Requirements

### Requirement: Bootstrap project command
Bootstrap MUST generate public-safe portable tracked configuration by default
and expose local absolute-path configuration only through explicit operator
opt-in.

#### Scenario: Default bootstrap creates portable tracked config
- **WHEN** an operator runs `bin/bootstrap-project /opt/example-project --name
  example-project --kind generic`
- **THEN** the generated tracked files use portable project scope instead of a
  machine-local absolute target path
- **AND** bootstrap still creates the required ChangeRail symlinks and helper
  wrappers

#### Scenario: Operator explicitly opts into local config
- **WHEN** an operator runs bootstrap with local absolute config mode
- **THEN** bootstrap renders machine-local absolute paths only after explicit
  opt-in
- **AND** it prints a warning before the suggested `git add` command

### Requirement: Bootstrap verification handoff
Bootstrap verification MUST validate the config model produced by bootstrap
before reporting success.

#### Scenario: Portable generated project is verified
- **WHEN** bootstrap completes default portable project generation
- **THEN** it runs `bin/verify-project <target>` and fails if portable scope
  validation fails
