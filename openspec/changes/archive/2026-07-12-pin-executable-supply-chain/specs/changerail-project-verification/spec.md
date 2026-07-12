## MODIFIED Requirements

### Requirement: Project-local config gates
Verification MUST fail closed when generated MCP config uses unpinned or
unlocked automatically executed npm package references.
Verification MUST compare tracked npm MCP integrity metadata with the npm
registry during trusted setup verification.

#### Scenario: Verifier checks MCP npm package pins
- **WHEN** `bin/verify-project <path>` inspects generated MCP config
- **THEN** it fails if an automatically executed npm MCP package is missing an
  exact version
- **AND** it fails if the package/version is absent from the tracked MCP npm
  integrity lock

#### Scenario: Verifier checks MCP npm integrity
- **WHEN** `bin/verify-project <path>` inspects generated MCP config in a
  trusted setup environment
- **THEN** it fails if tracked `mcp-npm-lock.json` integrity is not SRI-shaped
- **AND** it fails if `npm view <package>@<version> dist.integrity --json`
  returns different integrity for any referenced MCP package
