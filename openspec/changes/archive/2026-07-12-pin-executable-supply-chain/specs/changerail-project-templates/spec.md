## MODIFIED Requirements

### Requirement: Public-safe template content
Project templates MUST pin automatically executed npm MCP dependencies to exact
versions represented in a tracked integrity lock that is verified during trusted
setup.

#### Scenario: Generated MCP dependencies are exact-version pinned
- **WHEN** project templates render `.mcp.json` and `.codex/config.toml`
- **THEN** every automatically executed npm MCP package argument includes an
  exact version
- **AND** the package/version is represented in the tracked MCP npm integrity
  lock
- **AND** `verify-project` can compare that lock entry with npm registry
  `dist.integrity`
