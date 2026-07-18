## ADDED Requirements

### Requirement: Pre-review fix-budget recovery branching
ChangeRail methodology MUST distinguish pre-review implementation fix cycles
from post-review `NO-GO` rescue cycles and MUST route an exhausted fix budget to
one bounded recovery branch without treating it as a review verdict.

#### Scenario: Bounded local defect remains in the source card
- **WHEN** verification still fails after the configured fix-cycle budget and
  the remaining defect stays inside the declared capability, scope and
  authority with a concrete verification target
- **THEN** the supervising lifecycle may perform a bounded same-card micro-fix
- **AND** that continuation does not consume or impersonate a review `NO-GO`
  cycle

#### Scenario: Remaining work has independent scope
- **WHEN** the remaining work adds a capability, deliverable, acceptance scope
  or independently reviewable risk
- **THEN** the lifecycle MUST create a linked rescue/replacement card with
  source lineage, findings, retained evidence and verification floor
- **AND** it MUST order that card before blocked downstream work

#### Scenario: Blocker is external or unavailable
- **WHEN** progress requires unavailable infrastructure, external authority or
  another condition that implementation work cannot remove
- **THEN** the lifecycle MUST retain a `BLOCKED` or `NOT-VERIFIABLE` outcome and
  an explicit resume condition
- **AND** it MUST NOT create a chain of implementation rescue cards for the
  unchanged external blocker
