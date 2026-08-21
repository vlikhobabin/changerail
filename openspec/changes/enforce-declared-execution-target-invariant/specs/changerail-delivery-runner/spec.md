## ADDED Requirements

### Requirement: Runner SHALL retain exact execution target identity
Delivery runner SHALL capture canonical declared target identity at attempt
start и SHALL сохранять ее через single-card status, plan status, blocker и
resume lineage без physical endpoint или credentials.

#### Scenario: Identity остается стабильной
- **WHEN** preflight, child terminal status и current declaration содержат exact
  same id/fingerprint
- **THEN** lifecycle может продолжиться к review/publish gates

#### Scenario: Declaration drifted во время delivery
- **WHEN** current tracked target identity отличается от captured identity
- **THEN** runner завершает path как blocked
- **AND** не запускает downstream card и не публикует payload

### Requirement: Runner SHALL reject target substitution on resume
Single-card и package resume SHALL запускать retained payload только при exact
target identity match и SHALL NOT принимать evidence или CLI input как rebind
authority.

#### Scenario: Retained identity mismatch
- **WHEN** source status, current declaration или recovery evidence имеют
  разные target identities
- **THEN** resume fail closed до Codex launch со stable target-mismatch reason

#### Scenario: Explicit rebind выполнен
- **WHEN** оператор публикует новую tracked declaration
- **THEN** старый retained attempt остается non-resumable
- **AND** новый clean delivery получает новую captured identity
