## ADDED Requirements

### Requirement: Public release docs reflect current surface
ChangeRail public release docs MUST describe tracked runner, metrics, schema,
manifest, review-history, public-safety and finalization surfaces as current
when those files are present in the repository.

#### Scenario: Consumer reads current status
- **WHEN** a consumer reads `README.md`, `CHANGELOG.md`, compatibility notes or
  migration guide
- **THEN** implemented delivery runner, metrics, manifest/review contracts,
  aliases, public-safety scan helper and publish finalization behavior are not
  described as future planned work

### Requirement: Drift command documentation
Release and user-facing docs MUST describe `scripts/smoke-drift.py` as an
inventory-driven gate unless it is invoked through a generated public-safe
fixture wrapper or baseline command.

#### Scenario: Maintainer runs drift check manually
- **WHEN** the maintainer follows public docs for workspace drift
- **THEN** the docs show `--config`, `--workspace-root` or `--project`
  invocation
- **AND** local release baseline docs explain that generated fixture coverage is
  used for public CI/local smoke
