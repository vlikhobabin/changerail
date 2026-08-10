## ADDED Requirements

### Requirement: Consumer lock and source drift verification
`verify-project` MUST validate `changerail.consumer-lock.v1` separately from
actual wiring and source revision checks. Broken wiring MUST always be blocking;
source drift MUST be non-blocking for advisory enforcement and blocking for
strict enforcement.

#### Scenario: Locked source and wiring match
- **WHEN** the consumer lock, actual symlinks and ChangeRail version/revision
  match
- **THEN** lock, wiring and source checks pass independently

#### Scenario: Advisory source revision drifts
- **WHEN** actual ChangeRail revision differs from an advisory lock while wiring
  remains valid
- **THEN** verification returns a visible non-blocking source-drift diagnostic

#### Scenario: Strict source revision drifts
- **WHEN** actual ChangeRail revision differs from a strict lock
- **THEN** verification reports a blocking source-drift failure with lock refresh
  remediation

#### Scenario: Wiring is broken under advisory enforcement
- **WHEN** an owned symlink is missing or resolves to an unexpected source
- **THEN** verification fails regardless of advisory source enforcement

### Requirement: Lockless consumer compatibility
Existing consumers without `openspec/changerail-consumer-lock.json` MUST remain
verifiable through the existing wiring contract and MUST receive an explicit
lockless compatibility diagnostic rather than an inferred strict lock.

#### Scenario: Existing consumer has no lock
- **WHEN** verify-project inspects a valid legacy POSIX consumer
- **THEN** existing wiring checks continue to apply
- **AND** absence of the new lock alone is not a blocking failure
