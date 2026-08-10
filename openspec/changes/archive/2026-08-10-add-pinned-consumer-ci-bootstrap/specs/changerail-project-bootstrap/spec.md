## ADDED Requirements

### Requirement: Explicit pinned consumer CI bootstrap
`bootstrap-project` MUST generate consumer CI only after explicit `--with-ci`
selection and MUST require a schema-valid strict consumer lock with an exact
ChangeRail revision. Invalid combinations MUST fail before target mutation.

#### Scenario: Operator opts into CI
- **WHEN** an operator bootstraps with `--with-ci` and strict lock enforcement
- **THEN** the target receives the tracked consumer CI workflow
- **AND** dry-run reports the workflow, lock and exact-revision requirements

#### Scenario: CI is requested with advisory lock
- **WHEN** `--with-ci` is combined with advisory or absent lock enforcement
- **THEN** bootstrap exits non-zero before writing the target

#### Scenario: Default bootstrap omits CI
- **WHEN** an operator does not pass `--with-ci`
- **THEN** bootstrap does not generate a CI provider workflow

### Requirement: Consumer CI uses exact lock revision
Generated CI MUST read `changerail.consumer-lock.v1`, checkout the declared
ChangeRail source at the exact revision into a disposable path, perform bounded
lock-owned wiring repair and run consumer verification without delivery auth.

#### Scenario: Clean-clone CI executes
- **WHEN** generated CI runs for a committed consumer
- **THEN** it installs the exact locked ChangeRail revision
- **AND** `verify-project` and the declared consumer baseline run from the clean
  clone

#### Scenario: Locked revision cannot be obtained
- **WHEN** the exact source revision is absent or unavailable
- **THEN** CI fails before wiring repair or verification with an actionable
  source diagnostic
