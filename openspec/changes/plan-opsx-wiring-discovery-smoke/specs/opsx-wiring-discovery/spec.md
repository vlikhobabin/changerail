## ADDED Requirements

### Requirement: Consumer wiring contract
OPSX MUST define how consumer projects expose OPSX skills and command wrappers
without requiring undocumented root paths.

#### Scenario: Consumer project wires Claude surface
- **WHEN** a consumer project follows OPSX wiring
- **THEN** Claude commands resolve from `.claude/commands/opsx` and skills
  resolve from `.claude/skills`

#### Scenario: Consumer project wires Codex surface
- **WHEN** a consumer project follows OPSX wiring
- **THEN** Codex skills resolve from `.codex/skills/opsx-*` entries without
  committing Codex runtime state

### Requirement: Repo-local dogfooding wiring
OPSX MUST define repo-local dogfooding wiring for `/opt/opsx` without symlinks
to private workspaces.

#### Scenario: OPSX repository enables its own minimal surface
- **WHEN** `/opt/opsx` enables local discovery for OPSX skills or commands
- **THEN** public tracked files contain only relative links, generated wiring or
  documented generic `/opt/opsx` references

### Requirement: Discovery smoke evidence
OPSX MUST require smoke evidence that `opsx-explore` and `opsx-ff` are
discoverable through the documented Claude and Codex wiring surfaces.

#### Scenario: Discovery smoke runs for minimal OPSX surface
- **WHEN** wiring smoke is executed
- **THEN** a JSON report is written under ignored runtime space with schema
  `opsx.wiring-discovery-smoke.v1`
- **AND** the report records repo-local and consumer-example checks for Claude
  command/skill discovery and Codex skill discovery
- **AND** each check records name, path, expected target, resolved target,
  status and message

### Requirement: Smoke pass criteria
OPSX MUST define deterministic pass/fail criteria for wiring discovery smoke.

#### Scenario: Smoke evaluates Claude wiring
- **WHEN** Claude wiring smoke runs
- **THEN** `.claude/skills` and `.claude/commands/opsx` resolve to the expected
  OPSX source directories
- **AND** `/opsx:explore` and `/opsx:ff` wrappers do not require a consumer-root
  `skills/` path

#### Scenario: Smoke evaluates Codex wiring
- **WHEN** Codex wiring smoke runs
- **THEN** `.codex/skills/opsx-explore` and `.codex/skills/opsx-ff` resolve to
  the expected OPSX source directories
- **AND** each resolved skill has a `SKILL.md` with matching frontmatter `name`

### Requirement: Public-safe wiring artifacts
OPSX wiring docs and smoke artifacts committed to the repository MUST avoid
private workspace names, machine-specific paths, secrets, local settings and
runtime state.

#### Scenario: Public-surface scan runs for wiring changes
- **WHEN** wiring docs or smoke scripts are prepared for commit
- **THEN** scan output contains no private workspace names or local-only state
