## ADDED Requirements

### Requirement: Retained-payload resume validation contract
`changerail.delivery-run.v1` resume checks MUST represent retained-payload
resume validation as structured preflight checks with stable machine reasons.
The contract MUST distinguish prior-status invalidity, card mismatch, workspace
mismatch, missing retained identity, payload drift, authorization absence,
authorization staleness, relation mismatch and authorization ceiling violation.

#### Scenario: Successful retained resume records fresh checks
- **WHEN** retained-payload resume validation succeeds
- **THEN** the resumed delivery-run status contains passing checks for prior
  status validation, retained-payload fingerprint validation and published
  investigation authorization validation
- **AND** those checks are fresh for the resumed run rather than copied as pass
  evidence from the prior blocked status

#### Scenario: Failed retained resume is machine-classified
- **WHEN** retained-payload resume validation fails for a known unsafe class
- **THEN** the resumed delivery-run status has `terminal_outcome: BLOCKED`
- **AND** `terminal_reason` is a stable lowercase machine value describing that
  class

### Requirement: Published authorization remains source of truth for retained resume
Retained-payload resume MUST use the published investigation authorization
contract as the only authority to cross the investigation-required boundary.
Authorization paths MUST be tracked under `openspec/board/4.done/`, clean at
`HEAD`, relation-matched to the successor card and within the declared ceiling.

#### Scenario: Stale authorization blocks retained resume
- **WHEN** the authorization card or investigation card is missing, outside
  `4.done`, untracked, modified in the index/worktree or stale relative to
  `HEAD`
- **THEN** retained-payload resume returns `BLOCKED`
- **AND** it does not launch review or publish

#### Scenario: Relation mismatch blocks retained resume
- **WHEN** the authorization source does not bind the exact investigation card,
  investigation id, successor card, successor id and reciprocal card links
- **THEN** retained-payload resume returns `BLOCKED`
- **AND** the status identifies the mismatch as authorization validation failure
