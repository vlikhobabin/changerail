## MODIFIED Requirements

### Requirement: Project-local config gates
Verification MUST accept portable project-local config only when its relative
scope resolves to the consumer project root.

#### Scenario: Portable config scope is valid
- **WHEN** verification inspects generated portable `.mcp.json`,
  `.codex/config.toml` and `openspec/config.yaml`
- **THEN** relative project scope is accepted only when it resolves to the
  consumer project root

#### Scenario: Unsafe portable config scope fails
- **WHEN** verification inspects config whose filesystem scope does not cover
  the consumer project root
- **THEN** `bin/verify-project` exits non-zero and reports the failed config
  scope check
