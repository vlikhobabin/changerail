## ADDED Requirements

### Requirement: Generated wiring drift and refresh discovery
Wiring discovery MUST expose whether generated Windows wiring is fresh, stale,
project-owned or using an explicit fallback mode.

#### Scenario: Discovery reports generated wiring freshness
- **WHEN** wiring discovery validates a generated Windows consumer
- **THEN** it reports generated-owned artifacts as fresh only when source
  identity and digest match the ChangeRail source of truth
- **AND** stale generated artifacts are reported with a refresh remediation

#### Scenario: Discovery reports fallback mode
- **WHEN** a Windows consumer uses symlink or junction fallback wiring
- **THEN** discovery reports the fallback mode separately from generated-copy
  wiring
- **AND** it identifies the source metadata and concrete per-check evidence
  required for that fallback to pass
