## ADDED Requirements

### Requirement: Recover a pre-group technical model failure
Runtime SHALL allow a single append-only technical recovery when a model session
fails before the next native task group starts, the failure is in the explicit
technical allowlist, payload and predecessor receipts are unchanged, and no writer,
review, final or publication intent is active.

#### Scenario: Capacity failure before next group
- **WHEN** completed groups and evidence exist but the next session exits with a
  recognized model capacity error before `change-N starting`
- **THEN** prepare/apply creates one successor linked by `recovery_of` and runs only
  the pending group with the fixed fallback model
- **AND** old run bytes, checkpoints, evidence, counters and review allowance remain unchanged

#### Scenario: Ambiguous or semantic failure
- **WHEN** the process may still be alive, failure is unknown, writer started, payload
  drifted, or the failure is a test/product/worker error
- **THEN** recovery is rejected before writer launch and no successor or allowance is created

#### Scenario: Repeat and concurrent apply
- **WHEN** the same receipt is applied again or two recoveries race
- **THEN** one attempt is retained; the same successor may be reconciled, while a
  second successor or changed model/payload is rejected
