## ADDED Requirements

### Requirement: Native Windows bootstrap entrypoint
ChangeRail MUST provide a tracked native Windows `.cmd` wrapper for the
bootstrap helper used to create generated-copy consumer projects.

#### Scenario: Maintainer inspects bootstrap wrapper
- **WHEN** a maintainer inspects the tracked `bin/` helper surface
- **THEN** `bin/bootstrap-project.cmd` exists
- **AND** it routes execution through `changerail-python.cmd`
- **AND** it propagates the helper exit code

#### Scenario: Clean-clone lifecycle invokes bootstrap natively
- **WHEN** the Windows clean-clone lifecycle proof bootstraps a disposable
  consumer project
- **THEN** it uses the cloned `bootstrap-project.cmd` native entrypoint
- **AND** it does not require direct execution of the extensionless POSIX
  `bin/bootstrap-project` script
