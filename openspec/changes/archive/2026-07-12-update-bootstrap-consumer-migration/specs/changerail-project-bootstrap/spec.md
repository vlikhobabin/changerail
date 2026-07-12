## ADDED Requirements

### Requirement: Bootstrap creates ChangeRail consumers
Bootstrap MUST generate new generic consumers wired to the ChangeRail source of
truth.

#### Scenario: Operator bootstraps a post-rename project
- **WHEN** an operator runs bootstrap with `/opt/changerail` as the source of
  truth
- **THEN** the generated project uses `/opt/changerail` in generated docs and
  config
- **AND** generated helper symlinks point to ChangeRail helper wrappers

#### Scenario: Existing target is non-empty
- **WHEN** bootstrap is run for a non-empty existing target
- **THEN** bootstrap continues to refuse overwrite unless explicit backup mode
  is requested
