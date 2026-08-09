## ADDED Requirements

### Requirement: Bootstrap maintenance opt-in
Bootstrap MUST provide an explicit `--with-maintenance` option that adds
repository knowledge maintenance wiring without changing the default generic
consumer output.

#### Scenario: Default bootstrap omits maintenance wiring
- **WHEN** an operator runs `bin/bootstrap-project /opt/example-project --name
  example-project --kind generic` without `--with-maintenance`
- **THEN** bootstrap does not create tracked maintenance policy, catalog,
  baseline, scheduler or helper declarations
- **AND** the generated project remains valid under existing verification
  behavior

#### Scenario: Operator opts into maintenance
- **WHEN** an operator runs `bin/bootstrap-project /opt/example-project --name
  example-project --kind generic --with-maintenance`
- **THEN** the target receives tracked maintenance policy/config skeletons,
  helper wiring and ignore rules required for maintenance runtime output
- **AND** bootstrap still runs `bin/verify-project <target>` unless explicitly
  skipped

### Requirement: Bootstrap maintenance opt-in stays orthogonal
Maintenance bootstrap wiring MUST be orthogonal to project `--kind`, surface
policy and Windows wiring backend decisions.

#### Scenario: Opt-in does not change project kind
- **WHEN** bootstrap renders a generic consumer with `--with-maintenance`
- **THEN** generated project kind remains `generic`
- **AND** maintenance wiring is represented as an additive opt-in surface

#### Scenario: Native Windows opt-in uses generated backend
- **WHEN** native Windows bootstrap selects generated-copy wiring and
  `--with-maintenance` is supplied
- **THEN** maintenance helper copies are included in generated ownership
  metadata
- **AND** no symlink or junction fallback is required solely for maintenance
  helpers
