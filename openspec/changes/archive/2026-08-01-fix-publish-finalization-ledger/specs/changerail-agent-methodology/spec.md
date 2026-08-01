## MODIFIED Requirements

### Requirement: Deterministic publish finalization helper
ChangeRail methodology MUST allow helper-assisted card finalization after a
reviewed payload commit, as long as the helper changes only stable board
metadata and ignored runtime manifest state. Exact mutable publication details
MUST be stored in ignored runtime manifest evidence rather than tracked card
text.

#### Scenario: Payload commit succeeds
- **WHEN** the reviewed payload commit is created for a card in `3.inprogress`
- **THEN** deterministic card metadata may be updated and amended without
  invalidating the reviewed payload
- **AND** the tracked card records stable final outcome and review/publish
  completion state without its own exact final commit hash
- **AND** the ignored manifest records the payload commit, final published
  commit, remote, branch, final status and timestamps for the operator and
  future review history

#### Scenario: Push-enabled publish completes
- **WHEN** a push-enabled publish reaches final remote update successfully
- **THEN** tracked done-card text does not retain mutable pending-push wording
- **AND** final push state is retained in the ignored delivery manifest ledger
