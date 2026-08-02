## ADDED Requirements

### Requirement: Drift gate classifies generated Windows wiring drift
The drift gate MUST classify stale, missing or project-owned generated Windows
wiring as broken wiring rather than a current ChangeRail source project.

#### Scenario: Generated Windows consumer is fresh
- **WHEN** `scripts/smoke-drift.py --project <path>` checks a generated Windows
  consumer whose `verify-project` summary passes
- **THEN** the project entry class is `changerail_source`
- **AND** the drift summary status is `pass`

#### Scenario: Generated Windows consumer is stale
- **WHEN** `scripts/smoke-drift.py --project <path>` checks a generated Windows
  consumer with stale generated wiring
- **THEN** the project entry class is `broken_wiring`
- **AND** the verifier summary or indicators identify stale generated wiring and
  refresh remediation

#### Scenario: Generated Windows consumer has project-owned divergence
- **WHEN** drift checks a generated Windows consumer whose wiring path has
  project-owned divergence
- **THEN** the project entry class is `broken_wiring`
- **AND** the drift gate exits non-zero instead of treating the project as
  connected to the current ChangeRail source
