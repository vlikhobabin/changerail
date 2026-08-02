## ADDED Requirements

### Requirement: Concrete generated Windows wiring ownership
The native Windows generated-copy default MUST use a concrete ownership model
that can be audited by bootstrap, verification, drift and future refresh logic.

#### Scenario: Generated copy ownership is inspected
- **WHEN** a maintainer inspects a generated Windows consumer
- **THEN** each generated wiring artifact has a tracked ownership record
- **AND** the record identifies artifact kind, project-relative destination,
  ChangeRail source identity, digest and generated owner state

#### Scenario: Generated default avoids link prerequisites
- **WHEN** generated-copy wiring is selected as the native Windows default
- **THEN** support does not depend on Developer Mode, administrator elevation,
  symlink privilege or junction traversal
- **AND** symlink and junction behavior remains outside the default path
