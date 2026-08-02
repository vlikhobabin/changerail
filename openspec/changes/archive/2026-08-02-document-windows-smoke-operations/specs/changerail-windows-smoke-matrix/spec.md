## ADDED Requirements

### Requirement: Windows smoke operations documentation
ChangeRail MUST document how maintainers run, interpret and retain evidence
from the Windows smoke matrix without exposing private Windows lab inventory.

#### Scenario: Maintainer runs local matrix
- **WHEN** a maintainer reads the Windows compatibility or release guidance
- **THEN** it shows the local deterministic matrix command
- **AND** it explains that local matrix success covers platform-neutral
  fixtures but does not by itself prove live host coverage

#### Scenario: Maintainer runs live matrix
- **WHEN** a maintainer reads the Windows live smoke guidance
- **THEN** it shows the live two-host command using ignored
  `internal/windows-lab-inventory.json`
- **AND** it identifies `windows-host-a` and `windows-host-b` as the only
  tracked host ids
- **AND** it explains repeat-after-cleanup expectations

#### Scenario: Maintainer interprets caveats
- **WHEN** a live host is unavailable or a matrix item fails
- **THEN** the documentation instructs maintainers to record a sanitized
  blocker or caveat before claiming host coverage
- **AND** it points to ignored `.runtime/changerail/windows-smoke/` reports as
  retained evidence

### Requirement: Windows smoke CI integration path
ChangeRail MUST document the boundary between current Linux release-baseline
matrix checks and future live Windows CI execution.

#### Scenario: Linux release baseline is documented
- **WHEN** release guidance describes local baseline checks
- **THEN** it includes the platform-neutral Windows smoke matrix command
- **AND** it states that this command does not require private Windows hosts

#### Scenario: Future Windows CI is documented
- **WHEN** Windows CI integration guidance is read
- **THEN** it describes runner-local secure inventory injection as future work
- **AND** it forbids committing SSH targets, usernames, credentials, private
  disposable roots or raw host output
