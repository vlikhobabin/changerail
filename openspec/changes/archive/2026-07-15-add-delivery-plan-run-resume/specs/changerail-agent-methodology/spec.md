## ADDED Requirements

### Requirement: Tracked queue runner methodology
ChangeRail methodology MUST describe the tracked queue runner as the generic
non-interactive mechanism for dependency-ordered delivery across independent
workspaces.

#### Scenario: Operator plans multi-workspace delivery
- **WHEN** a consumer needs dependency-ordered delivery across several
  independent git workspaces
- **THEN** methodology points to the queue plan runner commands instead of
  requiring a private supervisor
- **AND** it still states that each live card is delivered by the existing
  single-card runner

#### Scenario: Queue run reaches safety stop
- **WHEN** a queue child returns `NO-GO`, `BLOCKED` or inconsistent repository
  state
- **THEN** methodology describes fail-fast behavior and resume through the
  tracked aggregate status

#### Scenario: Queue work crosses repositories
- **WHEN** a plan contains cards from multiple child repositories
- **THEN** methodology keeps each repository as its own ChangeRail delivery
  unit and allows parallelism only across independent repositories
