## ADDED Requirements

### Requirement: Profile-aware consumer templates
Project templates MUST render the selected project topology, surface policy and
Codex authority as observable tracked configuration. Profiles MUST describe
repository ownership and agent authority without generating domain-specific
application code.

#### Scenario: Workspace root profile is rendered
- **WHEN** bootstrap selects `workspace-root`
- **THEN** generated guidance declares aggregator ownership and independent
  child-repository boundaries
- **AND** bootstrap does not create child repositories or application source

#### Scenario: Service profile is rendered
- **WHEN** bootstrap selects `service`
- **THEN** generated guidance declares single-repository delivery ownership
- **AND** no domain framework or deployment configuration is implied

#### Scenario: Codex-only surfaces are rendered
- **WHEN** bootstrap selects `codex-only`
- **THEN** tracked verification policy marks Codex required, Claude optional
  and legacy artifacts forbidden
- **AND** mandatory targeted OpenSpec validation remains required

### Requirement: Explicit Codex authority templates
The Codex config template MUST render `safe-interactive` as
`approval_policy = "on-request"` and `sandbox_mode = "workspace-write"`, and MUST
render `never`/`danger-full-access` only for explicit `trusted-automation`.

#### Scenario: Generic project uses safe authority
- **WHEN** a generic project is rendered with default options
- **THEN** its tracked Codex config does not grant unattended full access

#### Scenario: Automation project records explicit authority
- **WHEN** trusted automation is selected
- **THEN** generated guidance identifies the profile as an explicit operator
  choice and documents its risk boundary
