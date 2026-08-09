## ADDED Requirements

### Requirement: Maintenance adapter policy configuration
ChangeRail maintenance policy MUST allow optional adapter detector configuration
without adding language-specific analyzer dependencies to ChangeRail core.

#### Scenario: Adapter policy declares argv
- **WHEN** policy configures an adapter with id, argv array, timeout and
  detector options
- **THEN** policy validation accepts the adapter configuration
- **AND** rejects shell-string command configuration for adapter execution

#### Scenario: Minimal policy omits adapters
- **WHEN** a policy omits adapter configuration
- **THEN** existing catalog validation, index rendering and core scan behavior
  remain unaffected

### Requirement: Maintenance adapter execution boundary
The maintenance scan MUST execute configured adapters without a shell, from the
repository root, with a bounded timeout.

#### Scenario: Adapter exits successfully
- **WHEN** a configured adapter process exits zero with schema-valid JSON output
- **THEN** scan maps its findings into the maintenance scan report
- **AND** preserves repository-relative evidence paths after safe-path
  normalization

#### Scenario: Adapter times out
- **WHEN** a configured adapter exceeds its timeout
- **THEN** scan records a detector-error result for that adapter
- **AND** does not interpret the adapter as a green architecture result

### Requirement: Maintenance adapter failure handling
Adapter failure, invalid output or unsafe evidence MUST fail closed as detector
errors rather than successful detector results.

#### Scenario: Adapter exits non-zero
- **WHEN** a configured adapter exits with a non-zero status
- **THEN** scan records a detector-error result with the adapter id and failure
  class

#### Scenario: Adapter emits invalid JSON
- **WHEN** a configured adapter emits output that is not a schema-valid adapter
  result document
- **THEN** scan records a detector-error result
- **AND** the report does not treat the adapter as passing

#### Scenario: Adapter emits path escape
- **WHEN** an adapter finding includes an absolute path, traversal path or
  repository root escape
- **THEN** scan records a detector-error result for unsafe adapter output
- **AND** does not include the unsafe path as trusted finding evidence
