## ADDED Requirements

### Requirement: Bootstrap Codex auth handoff documentation
Bootstrap guidance MUST explain that generated consumers keep Codex auth state
ignored and that delivery runner auth setup is an explicit local operator
handoff.

#### Scenario: Operator reads bootstrap guidance
- **WHEN** an operator bootstraps or adopts a consumer project
- **THEN** the guidance states that `.codex/auth.json` must remain ignored and
  untracked
- **AND** it explains that bootstrap does not silently copy credentials by
  default
- **AND** it points to the manual or opt-in setup path for delivery runner auth
  readiness
