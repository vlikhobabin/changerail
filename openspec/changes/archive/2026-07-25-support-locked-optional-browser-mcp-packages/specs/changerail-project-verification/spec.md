## MODIFIED Requirements

### Requirement: Project-local config gates
Verification MUST parse project-local `.mcp.json`, `.codex/config.toml` and
`openspec/config.yaml`.
Verification MUST validate that generated config scopes filesystem access and
trusted project settings to the consumer project by default.
Verification MUST fail closed when generated MCP config uses unpinned or
unlocked automatically executed npm package references.
Verification MUST compare tracked npm MCP integrity metadata with the npm
registry during trusted setup verification.
Verification MUST recognize exact MCP npm package pins passed to `npx` as the
direct package argument, `--package=<package>@<version>` or
`--package <package>@<version>`.

#### Scenario: Config scope is project-local
- **WHEN** verification inspects MCP and Codex config
- **THEN** filesystem scope and trust settings cover the consumer project root
  instead of the ChangeRail repository root

#### Scenario: Verifier accepts locked direct and package-option pins
- **WHEN** `bin/verify-project <path>` inspects consumer MCP config containing
  `npx` commands for `@playwright/mcp@0.0.68` or
  `chrome-devtools-mcp@0.20.3`
- **AND** each package is passed as a direct package argument,
  `--package=<package>@<version>` or `--package <package>@<version>`
- **AND** each package/version is present in `mcp-npm-lock.json` with matching
  trusted npm registry integrity
- **THEN** package pin verification passes for those optional browser MCP
  entries

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
