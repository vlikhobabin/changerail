## ADDED Requirements

### Requirement: Fail-closed Windows link fallbacks
Native Windows symlink and junction wiring modes MUST remain explicit
fail-closed fallbacks rather than defaults.

#### Scenario: Symlink fallback is evaluated
- **WHEN** a consumer requests Windows symlink fallback
- **THEN** ChangeRail requires explicit operator opt-in and positive
  Developer Mode or privilege proof
- **AND** the proof includes source metadata and concrete per-check evidence,
  not only passed status names
- **AND** the fallback is rejected when that proof is unavailable or negative

#### Scenario: Junction fallback is evaluated
- **WHEN** a consumer requests Windows junction fallback
- **THEN** ChangeRail requires explicit operator opt-in, link-aware cleanup
  behavior and Git-safety preconditions
- **AND** the proof includes source metadata and concrete per-check evidence,
  not only passed status names
- **AND** the fallback is rejected when Git status, dry-run add or index
  evidence would include out-of-scope content

### Requirement: Generated wiring cleanup boundary
Windows wiring cleanup MUST be bounded to generated-owned or current-run-owned
artifacts.

#### Scenario: Cleanup runs after setup failure
- **WHEN** setup or refresh fails during Windows wiring
- **THEN** cleanup removes only artifacts created by the current run or
  explicitly marked generated-owned for the requested operation
- **AND** cleanup does not remove project-owned files or recurse through
  symlink or junction targets
