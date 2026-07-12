## ADDED Requirements

### Requirement: Delivery manifest derivation helper
ChangeRail MUST provide a helper command that can derive a delivery manifest
from a board card and the current workspace state.

#### Scenario: Delivery derives a card manifest
- **WHEN** an operator runs the manifest helper for a board card
- **THEN** the helper derives card id, card path, card status, ordered changes,
  archived change paths and dirty committable paths
- **AND** it excludes ignored runtime verdict and manifest paths from
  `committable_paths`

#### Scenario: Reviewer inspects derived staging plan
- **WHEN** a derived manifest is passed to `staging-plan`
- **THEN** the output is a deterministic list of repository-relative paths that
  can be audited before publish staging
