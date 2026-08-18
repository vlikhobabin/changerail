## MODIFIED Requirements

### Requirement: Consumer configuration verification
ChangeRail verification MUST check generated consumer configuration, executable
wiring, npm MCP pins and trusted registry integrity. Successful diagnostic
output on stderr MUST NOT be interpreted as part of a machine-readable stdout
payload.

#### Scenario: Successful npm warnings do not corrupt integrity verification
- **WHEN** `npm view <package>@<version> dist.integrity --json` exits zero,
  returns the locked integrity JSON in stdout and emits a warning in stderr
- **THEN** `bin/verify-project` compares only the stdout payload with the lock
- **AND** the stderr warning does not produce a false integrity mismatch
