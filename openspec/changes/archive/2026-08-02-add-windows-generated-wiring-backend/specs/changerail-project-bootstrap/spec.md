## ADDED Requirements

### Requirement: Native Windows generated wiring backend
Bootstrap MUST select generated project-local wiring as the default backend on
native Windows without requiring Developer Mode, administrator elevation,
symlink privileges or junction traversal.

#### Scenario: Native Windows bootstrap selects generated wiring
- **WHEN** an operator runs `bin/bootstrap-project` for a generic consumer on a
  native Windows platform without an explicit wiring override
- **THEN** bootstrap creates generated project-local command, skill and helper
  wiring artifacts
- **AND** it does not create symlinks or junctions for ChangeRail wiring

#### Scenario: Non-Windows bootstrap preserves existing wiring
- **WHEN** an operator runs `bin/bootstrap-project` on a non-Windows platform
  without an explicit wiring override
- **THEN** bootstrap keeps the existing POSIX symlink wiring behavior
- **AND** generated-copy Windows policy does not remove or weaken the existing
  symlink contract

### Requirement: Generated wiring ownership metadata
Bootstrap MUST record verifier-readable generated ownership metadata for
generated Windows wiring artifacts.

#### Scenario: Generated artifact is written
- **WHEN** bootstrap writes a generated command, skill or helper wiring artifact
- **THEN** tracked project policy records the project-relative artifact path
- **AND** it records whether the artifact is file wiring or directory wiring
- **AND** it records ChangeRail source identity and digest data sufficient for
  later stale-copy verification
- **AND** it marks the artifact as generated-owned rather than project-owned

#### Scenario: Portable bootstrap writes ownership metadata
- **WHEN** bootstrap runs in portable config mode
- **THEN** generated ownership metadata avoids machine-local absolute paths
- **AND** source identity is expressed relative to the linked ChangeRail source
  of truth

### Requirement: Wiring backend dry-run reporting
Bootstrap dry-run output MUST report the selected wiring backend, generated
ownership plan and fallback reasons.

#### Scenario: Operator previews native Windows bootstrap
- **WHEN** bootstrap is run with `--dry-run` on native Windows
- **THEN** the plan reports the generated-copy backend
- **AND** it lists generated command, skill and helper wiring artifacts
- **AND** it explains that symlink and junction modes were not selected because
  no explicit fallback opt-in was supplied
