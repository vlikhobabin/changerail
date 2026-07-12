## ADDED Requirements

### Requirement: Deterministic publish finalization helper
ChangeRail methodology MUST allow helper-assisted card finalization after a
reviewed payload commit, as long as the helper changes only deterministic board
metadata and ignored runtime manifest state.

#### Scenario: Payload commit succeeds
- **WHEN** the reviewed payload commit is created for a card in `3.inprogress`
- **THEN** deterministic card metadata may be updated and amended without
  invalidating the reviewed payload
- **AND** the finalization records the final commit/push metadata for the
  operator and future review history
