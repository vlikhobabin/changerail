## ADDED Requirements

### Requirement: Consumer Codex auth setup documentation
ChangeRail runner documentation MUST describe the Codex auth prerequisite for
single-card and plan-oriented delivery runner commands without making
credentials part of the tracked repository surface.

#### Scenario: Operator reads runner auth setup
- **WHEN** an operator reads the delivery runner or consumer adoption docs
- **THEN** the docs explain that `run`, `preflight-plan`, `run-plan` and
  `resume-plan` require an effective Codex auth source before unattended
  delivery can launch
- **AND** the docs describe default `<workspace>/.codex` `CODEX_HOME`
  resolution and explicit `CODEX_HOME` override behavior

#### Scenario: Documentation gives safe remediation examples
- **WHEN** the docs describe missing-auth remediation
- **THEN** examples use generic paths such as `/opt/example-project` and
  `$HOME`
- **AND** examples include a project-local ignored auth marker symlink and an
  explicit `CODEX_HOME` invocation
- **AND** the docs do not instruct operators to commit credentials or runtime
  auth state
