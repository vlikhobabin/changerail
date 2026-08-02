## ADDED Requirements

### Requirement: Generated Windows wiring discovery
Wiring discovery MUST recognize generated project-local command, skill and
helper wiring as the native Windows default for generated consumers.

#### Scenario: Consumer uses generated Windows wiring
- **WHEN** wiring discovery or smoke validates a generated native Windows
  consumer
- **THEN** command, skill and helper surfaces may be generated project-local
  files or directories rather than symlinks
- **AND** the generated surfaces are accepted only when tracked ownership
  metadata identifies their ChangeRail source identity

#### Scenario: Generated surfaces are classified
- **WHEN** discovery reports generated Windows wiring
- **THEN** directory surfaces and file surfaces are classified separately
- **AND** the report distinguishes generated-copy wiring from symlink and
  junction fallback modes

### Requirement: POSIX discovery compatibility
Wiring discovery MUST preserve existing POSIX symlink discovery behavior while
adding generated Windows wiring.

#### Scenario: POSIX consumer uses symlink wiring
- **WHEN** wiring discovery validates an existing POSIX-generated consumer
- **THEN** symlink-based `.claude`, `.codex` and `bin/` wiring continues to pass
- **AND** generated Windows wiring checks do not require POSIX consumers to copy
  ChangeRail-owned surfaces
