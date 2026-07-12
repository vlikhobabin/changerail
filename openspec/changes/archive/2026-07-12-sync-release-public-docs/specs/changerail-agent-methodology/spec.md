## ADDED Requirements

### Requirement: Repository public surface inventory stays current
ChangeRail repository instructions MUST classify currently tracked templates,
bootstrap helpers, verification helpers, release/drift scripts, runner,
metrics and contract schemas as current public surface rather than planned
surface.

#### Scenario: Agent reads repository instructions
- **WHEN** an agent reads root `AGENTS.md`
- **THEN** it can identify the current public ChangeRail-owned surface without
  treating already tracked templates, bootstrap helpers, verification helpers
  or scripts as future work
