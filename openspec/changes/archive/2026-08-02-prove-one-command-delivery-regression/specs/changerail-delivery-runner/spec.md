## ADDED Requirements

### Requirement: One-command delivery regression smoke
ChangeRail MUST provide deterministic delivery-runner smoke coverage that starts
from a deliver-ready board card and proves the runner-supervised
`$changerail-deliver` path through observable repository and runtime state.

#### Scenario: One-command delivery success fixture
- **WHEN** the delivery runner smoke runs its one-command success fixture
- **THEN** the fixture uses a temporary Git repository and local bare remote
  without live network access
- **AND** the fixture starts from a `2.todo` deliver-ready card and invokes one
  runner orchestration entrypoint for that card
- **AND** the final card location, local Git history, remote branch, delivery
  manifest, review verdict, retained evidence and runner status are mutually
  consistent
- **AND** tracked card text does not contain stale mutable publish metadata such
  as exact commit hash or push status
- **AND** manifest scope excludes ignored runtime evidence and contains no extra
  committable paths outside the card-owned payload

#### Scenario: One-command delivery resumes after transient preflight
- **WHEN** the smoke simulates a transient remote publish-target preflight
  failure before launch
- **THEN** the first runner status records a blocked preflight with sanitized
  remote failure evidence
- **AND** an explicit `resume --status-path <status.json>` run repeats fresh
  preflight and publishes only after the local bare remote is reachable
- **AND** the resumed terminal status is `DELIVERED` for the same card

#### Scenario: One-command delivery fails closed on stale verdict
- **WHEN** the smoke provides a stale canonical review verdict for an unpublished
  card after a child exits successfully without authoritative delivery evidence
- **THEN** the runner records `BLOCKED`
- **AND** the card remains outside `4.done`
- **AND** no payload commit is pushed to the local bare remote

#### Scenario: One-command delivery fails closed on exhausted review budget
- **WHEN** the smoke simulates a final external review `NO-GO` after the
  same-card review rescue budget is exhausted
- **THEN** the runner records `NO-GO` or a documented review-gated blocked
  terminal outcome
- **AND** the card remains unpublished
- **AND** no payload commit is pushed to the local bare remote
