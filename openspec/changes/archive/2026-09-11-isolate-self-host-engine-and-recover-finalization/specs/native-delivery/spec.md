## ADDED Requirements

### Requirement: Isolate self-host engine identity
Runtime SHALL execute self-host delivery from an immutable, hash-identified engine
snapshot separate from the mutable project checkout; drift of engine, launcher,
profile or binding SHALL block execution.

#### Scenario: Mutable project with pinned engine
- **WHEN** product runtime files change during self-host delivery while the pinned
  engine inventory remains unchanged
- **THEN** execution continues with the pinned engine and records separate engine and
  project identities

### Requirement: Recover self-host run into one successor
Runtime SHALL provide append-only prepare/apply/reconcile recovery that records the
complete predecessor inventory, accepted plan, corrective delta, engine identity and
review accounting, then atomically creates at most one successor.

#### Scenario: Finalize without replay
- **WHEN** a stopped self-host run has completed groups and no writer or review intent
- **THEN** one successor is created, history and accounting are retained, completed
  groups are not replayed, and the successor enters the normal finalize lifecycle.

#### Scenario: Drift, race or boundary violation
- **WHEN** engine/project inputs drift, a process is live, verification is unresolved,
  or review/final/archive/publication has begun
- **THEN** recovery fails closed without a second successor or new review allowance.
