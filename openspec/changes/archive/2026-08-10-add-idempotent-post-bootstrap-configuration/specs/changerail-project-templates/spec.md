## ADDED Requirements

### Requirement: Optional generated consumer README
The template set MUST provide a minimal public-safe consumer README that is
rendered only through explicit bootstrap opt-in and is never used as an
overwrite source for an existing README.

#### Scenario: README opt-in is rendered
- **WHEN** a new empty consumer selects README generation
- **THEN** the file identifies the project, selected ChangeRail profile and
  local verification command
- **AND** it contains no machine-local path, private remote or credential data

#### Scenario: README already exists
- **WHEN** bootstrap or configure sees an existing README
- **THEN** it preserves the file and reports the ownership conflict rather than
  replacing it

### Requirement: Generated Git handoff guidance
Generated guidance MUST distinguish local Git initialization from commit and
publication and MUST state the exact remaining operator actions.

#### Scenario: Git repository is initialized
- **WHEN** bootstrap performs explicit local Git initialization
- **THEN** completion output states that no files were staged, committed or
  pushed
- **AND** commit/push remain separate operator actions
