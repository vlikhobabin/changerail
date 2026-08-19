## ADDED Requirements

### Requirement: Runner provides child discovery budget policy
The delivery runner MUST provide runner-launched children with a compact
public-safe discovery budget or policy that describes bounded output
expectations.

#### Scenario: Runner launches delivery child
- **WHEN** the runner starts a non-interactive delivery child
- **THEN** the child receives a discovery policy through prompt text,
  environment or another structured handoff available to the child
- **AND** the policy identifies bounded discovery patterns and the documented
  per-command output threshold

#### Scenario: Policy is generic across consumer repositories
- **WHEN** the runner prepares the child discovery policy
- **THEN** the policy avoids codebase-language assumptions, private workspace
  names and raw runtime log content
- **AND** the policy does not require shell interception to be enforceable

#### Scenario: Raw evidence is retained separately
- **WHEN** command stdout or stderr is retained for runtime evidence
- **THEN** the discovery policy does not make ignored raw evidence committable
- **AND** the child-facing policy remains a bounded summary of expected
  behavior rather than a copy of raw command output
