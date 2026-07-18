## ADDED Requirements

### Requirement: Generated consumers receive fix-budget recovery guidance
Project templates MUST explain the distinction between implementation fix
cycles and independent-review rescue cycles and MUST retain the shared
autonomous recovery branches.

#### Scenario: Consumer AGENTS guidance is generated
- **WHEN** bootstrap renders `AGENTS.md` for a consumer project
- **THEN** generated guidance identifies `max-fix-cycles` as a pre-review
  implement/verify bound and `max-review-cycles` as a post-review rescue bound
- **AND** it names `fix_budget_exhausted` as a non-delivered handoff

#### Scenario: Generated agent chooses recovery scope
- **WHEN** a generated consumer agent reads the delivery rules after fix-budget
  exhaustion
- **THEN** it is directed to choose bounded same-card micro-fix, linked
  rescue/replacement card or external blocker according to observable scope
- **AND** manual exceptional budget is not described as the default path
