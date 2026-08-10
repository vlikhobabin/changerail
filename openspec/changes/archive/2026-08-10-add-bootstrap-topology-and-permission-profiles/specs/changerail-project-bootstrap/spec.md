## ADDED Requirements

### Requirement: Bootstrap topology, surface and Codex authority profiles
`bootstrap-project` MUST accept canonical project, surface and Codex authority
profiles, normalize them before target mutation and render the selected policy
as tracked consumer configuration. The public default MUST use `generic`,
`all-surfaces` and `safe-interactive`; `trusted-automation` MUST require explicit
operator selection.

#### Scenario: Operator uses public defaults
- **WHEN** an operator bootstraps a project without profile flags
- **THEN** bootstrap selects `generic`, `all-surfaces` and `safe-interactive`
- **AND** generated Codex policy uses `on-request` and `workspace-write`

#### Scenario: Operator explicitly selects trusted automation
- **WHEN** an operator passes `--codex-policy trusted-automation`
- **THEN** generated Codex policy uses `never` and `danger-full-access`
- **AND** dry-run reports that authority choice before writing files

#### Scenario: Profile combination is invalid
- **WHEN** an operator supplies an unknown profile or conflicting canonical and
  legacy values
- **THEN** bootstrap exits non-zero before creating or modifying the target

### Requirement: Legacy kind compatibility
`bootstrap-project` MUST retain `--kind` as a bounded compatibility alias for
supported project profiles while generated artifacts and documentation use the
canonical profile terminology.

#### Scenario: Legacy generic bootstrap runs
- **WHEN** an existing script passes `--kind generic` and no conflicting
  `--profile`
- **THEN** bootstrap normalizes the value to profile `generic`
- **AND** generated project behavior matches the canonical profile

#### Scenario: Legacy alias conflicts with canonical profile
- **WHEN** `--kind generic` and `--profile service` are supplied together
- **THEN** bootstrap fails before target mutation with an actionable conflict
  diagnostic
