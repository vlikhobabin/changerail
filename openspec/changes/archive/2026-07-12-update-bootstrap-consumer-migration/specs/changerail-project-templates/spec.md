## ADDED Requirements

### Requirement: Templates render ChangeRail placeholders
Project templates MUST use ChangeRail placeholder names and generated prose
after the rename.

#### Scenario: Template is rendered
- **WHEN** bootstrap renders project templates
- **THEN** placeholders such as `{{CHANGERAIL_ROOT}}` are resolved to the
  configured ChangeRail source-of-truth path
- **AND** generated `AGENTS.md` and `CLAUDE.md` refer to ChangeRail, not OPSX,
  except explicit migration notes

#### Scenario: Claude command list is generated
- **WHEN** `CLAUDE.md` is generated for a consumer project
- **THEN** it lists `/changerail:*` lifecycle commands
