## ADDED Requirements

### Requirement: Generated Windows wiring refresh
Bootstrap or its refresh surface MUST update only generated-owned Windows
wiring artifacts and MUST NOT silently overwrite project-owned files.

#### Scenario: Generated wiring is refreshed
- **WHEN** an operator runs the generated Windows wiring refresh operation
- **THEN** only artifacts recorded as generated-owned are updated from the
  ChangeRail source of truth
- **AND** refreshed artifacts receive updated digest metadata
- **AND** ignored runtime state and credentials are left untouched

#### Scenario: Project-owned file diverges
- **WHEN** a target path contains project-owned content or lacks generated
  ownership metadata
- **THEN** refresh refuses to overwrite that path silently
- **AND** the output identifies the project-owned divergence and remediation
  path

### Requirement: Partial failure rollback for Windows wiring
Bootstrap MUST roll back only artifacts created by the current run after a
partial Windows wiring failure.

#### Scenario: Generated bootstrap fails partway through
- **WHEN** native Windows generated wiring setup fails after creating some
  artifacts
- **THEN** cleanup removes only artifacts created by the current bootstrap run
- **AND** preexisting project-owned files, ignored runtime state and
  credentials remain untouched

#### Scenario: Cleanup sees a link path
- **WHEN** rollback encounters a symlink or junction path
- **THEN** cleanup removes the link itself when it was created by the current
  run
- **AND** it does not recurse into the link target

### Requirement: Explicit Windows wiring fallback controls
Bootstrap MUST require explicit operator opt-in before creating Windows symlink
or junction fallback wiring.

#### Scenario: Symlink fallback is requested
- **WHEN** an operator explicitly requests Windows symlink fallback
- **THEN** bootstrap verifies symlink privilege or Developer Mode proof before
  reporting success
- **AND** proof reports MUST include schema-valid source metadata and concrete
  per-check evidence, not only passed status names
- **AND** failure to prove the required capability exits non-zero

#### Scenario: Junction fallback is requested
- **WHEN** an operator explicitly requests Windows junction fallback
- **THEN** bootstrap verifies link-aware cleanup and Git-safety preconditions
  before reporting success
- **AND** proof reports MUST include schema-valid source metadata and concrete
  per-check evidence, not only passed status names
- **AND** failure to prove those preconditions exits non-zero
