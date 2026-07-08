## ADDED Requirements

### Requirement: Consumer project verification gate
OPSX MUST provide `bin/verify-project <path>` as a red/green gate for consumer
project wiring and baseline configuration.

#### Scenario: Valid consumer project passes verification
- **WHEN** `bin/verify-project /opt/example-project` runs against a correctly
  wired consumer project
- **THEN** it exits `0` after checking symlink-и, configs, OpenSpec validation,
  helper/schema reachability and ignored runtime/auth paths

#### Scenario: Invalid consumer project fails verification
- **WHEN** required OPSX wiring, config or ignore policy is missing
- **THEN** `bin/verify-project` exits non-zero and reports the failed check

### Requirement: OPSX source resolution
Verification MUST accept OPSX-owned surfaces that resolve directly to
`/opt/opsx` or through an explicitly documented aggregator path.

#### Scenario: Consumer uses direct OPSX wiring
- **WHEN** a required symlink resolves under `/opt/opsx`
- **THEN** verification treats the path as valid OPSX source wiring

#### Scenario: Consumer uses aggregator wiring
- **WHEN** an operator passes `--aggregator-root <path>` and required symlink-и
  resolve through that root to OPSX-owned surfaces
- **THEN** verification treats the path as valid aggregator wiring

### Requirement: Project-local config gates
Verification MUST parse project-local `.mcp.json`, `.codex/config.toml` and
`openspec/config.yaml`.

#### Scenario: Config scope is project-local
- **WHEN** verification inspects MCP and Codex config
- **THEN** filesystem scope and trust settings cover the consumer project root
  instead of the OPSX repository root

### Requirement: Runtime/auth ignore policy
Verification MUST fail when consumer projects do not ignore OPSX runtime,
agent session and auth paths.

#### Scenario: Runtime path would be committed
- **WHEN** `.runtime/`, `.artifacts/`, `.ai/`, Codex runtime/auth state or
  Claude local settings are not ignored
- **THEN** `bin/verify-project` exits non-zero
