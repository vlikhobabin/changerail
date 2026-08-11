## ADDED Requirements

### Requirement: Versioned release metadata
Before publishing a ChangeRail release, release metadata MUST name the release
version, summarize user-facing changes since the previous release, include
operator migration notes and pass the local release baseline.

#### Scenario: Release metadata is ready
- **WHEN** a maintainer publishes `0.5.0`
- **THEN** `VERSION`, `CHANGELOG.md`, compatibility notes and migration guide
  all identify `0.5.0`
- **AND** `CHANGELOG.md` has an empty `Unreleased` section for future work
- **AND** the release card records the verification commands and observed
  outcomes used before publish
