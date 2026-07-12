## ADDED Requirements

### Requirement: Bootstrap smoke checks workflow guidance
Bootstrap smoke MUST verify that generated consumer files include current
ChangeRail workflow guidance.

#### Scenario: Bootstrap smoke renders a generic consumer
- **WHEN** `python3 scripts/smoke-bootstrap-project.py` runs
- **THEN** it checks generated `AGENTS.md` and `openspec/board/README.md`
- **AND** it fails if lifecycle, role model, fresh review gate or board
  finalization guidance is missing
