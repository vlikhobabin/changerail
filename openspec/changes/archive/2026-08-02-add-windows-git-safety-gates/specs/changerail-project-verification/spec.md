## ADDED Requirements

### Requirement: Windows wiring Git safety verification
`verify-project` and its focused smoke coverage MUST prove Windows wiring paths
are safe to stage using Git porcelain status, dry-run add and index inspection.

#### Scenario: Generated wiring is Git-safe
- **WHEN** a generated Windows consumer fixture is inspected
- **THEN** verification evidence includes `git status --porcelain`,
  `git add --dry-run` and index inspection for generated command, skill and
  helper paths
- **AND** no evidence would stage ChangeRail source, ignored runtime state,
  credentials or out-of-scope files

#### Scenario: Symlink fallback Git safety is checked
- **WHEN** a Windows symlink fallback fixture is inspected
- **THEN** Git safety evidence proves the link path itself is stageable only
  within the consumer project scope
- **AND** unsafe traversal into ChangeRail source or ignored runtime state is a
  blocking failure

#### Scenario: Junction fallback Git safety is checked
- **WHEN** a Windows junction fallback fixture is inspected
- **THEN** Git safety evidence includes porcelain status, dry-run add and index
  inspection for the junction path class
- **AND** any evidence that would stage out-of-scope content is a blocking
  failure

#### Scenario: Credentials are not exposed
- **WHEN** Git safety fixtures include credential-like ignored files
- **THEN** diagnostics do not print credential contents
- **AND** the checks fail closed if the credential-like path becomes stageable
