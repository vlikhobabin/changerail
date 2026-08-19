## ADDED Requirements

### Requirement: Adopted consumer lock verification
`verify-project` MUST distinguish legacy lockless compatibility from adopted
lock-backed wiring. After successful adoption, verification MUST validate the
consumer lock, adopted wiring inventory and source revision according to the
selected enforcement.

#### Scenario: Legacy lockless consumer remains diagnostic
- **WHEN** `verify-project` inspects a valid legacy consumer without
  `openspec/changerail-consumer-lock.json`
- **THEN** existing lockless compatibility checks remain visible
- **AND** the output does not claim that lock-backed refresh is available

#### Scenario: Adopted consumer is lock-backed
- **WHEN** `verify-project` inspects a consumer migrated by lockless adoption
- **THEN** it validates `openspec/changerail-consumer-lock.json`
- **AND** it validates that adopted wiring matches the lock-owned artifact
  inventory
- **AND** it reports source drift according to advisory or strict enforcement

#### Scenario: Adopted helper is missing
- **WHEN** a helper listed in the adopted consumer lock is missing or no longer
  matches declared ownership
- **THEN** verification reports a blocking wiring failure
- **AND** the remediation points to lock-owned `--refresh-wiring`, not another
  lockless adoption

### Requirement: Lockless adoption diagnostics
`verify-project` MUST report whether a lockless consumer appears eligible for
explicit adoption without recommending automatic overwrite for ambiguous or
project-owned surfaces.

#### Scenario: Lockless consumer appears adoptable
- **WHEN** a lockless consumer has complete required wiring resolving to one
  ChangeRail source root and no project-owned conflicts
- **THEN** verification may report an adoption advisory with a generic
  existing-project adoption command
- **AND** the advisory omits private paths and credential values

#### Scenario: Lockless consumer has ambiguous ownership
- **WHEN** verification finds dangling wiring, mixed roots, regular files or
  undeclared destinations in the wiring surface
- **THEN** it reports that automatic adoption is unsafe
- **AND** it does not recommend a command that would overwrite project-owned
  content
