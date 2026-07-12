## ADDED Requirements

### Requirement: Drift gate classifies ChangeRail consumers
Workspace drift checks MUST classify post-rename consumers against the
ChangeRail source of truth.

#### Scenario: Drift gate checks a valid consumer
- **WHEN** drift smoke checks a project wired to `/opt/changerail`
- **THEN** it reports the project as a ChangeRail consumer with passing wiring

#### Scenario: Drift gate checks stale OPSX wiring
- **WHEN** drift smoke checks a project still wired to `/opt/opsx`
- **THEN** it reports stale or legacy wiring instead of passing the project as
  current
