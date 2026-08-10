## ADDED Requirements

### Requirement: Declared bootstrap profile verification
`verify-project` MUST validate the canonical project, surface and Codex authority
profiles recorded by bootstrap and MUST fail closed when generated configuration
contradicts the declared profile. Legacy consumers without canonical fields MUST
continue through the existing all-surfaces compatibility path.

#### Scenario: Codex-only consumer is coherent
- **WHEN** a consumer declares `codex-only` and contains valid Codex wiring but
  omits optional Claude wiring
- **THEN** verification reports the optional surface as a non-blocking
  diagnostic
- **AND** the profile consistency check passes

#### Scenario: Safe profile contains full-access settings
- **WHEN** a consumer declares `safe-interactive` but tracked Codex config uses
  `never` or `danger-full-access`
- **THEN** verification reports a blocking profile mismatch

#### Scenario: Legacy consumer has no canonical profiles
- **WHEN** an existing consumer has no new bootstrap profile metadata
- **THEN** verification applies the existing strict all-surfaces behavior
- **AND** does not infer trusted automation from absent metadata

### Requirement: Profile matrix regression evidence
ChangeRail MUST maintain deterministic smoke coverage for all supported project,
surface and Codex authority selections and their invalid combinations.

#### Scenario: Profile smoke runs
- **WHEN** bootstrap and verify smoke execute
- **THEN** default, codex-only, workspace-root, service and trusted-automation
  fixtures are evaluated
- **AND** invalid or conflicting values fail before target mutation
