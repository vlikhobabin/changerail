## ADDED Requirements

### Requirement: Generated Windows wiring verification
`verify-project` MUST verify generated Windows wiring ownership, freshness and
project-owned divergence when a consumer declares generated wiring policy.

#### Scenario: Generated wiring is fresh
- **WHEN** `bin/verify-project <path>` inspects a consumer with generated
  Windows wiring policy
- **THEN** each generated-owned command, skill and helper artifact matches the
  recorded source identity and digest
- **AND** verification passes that wiring check

#### Scenario: Generated wiring is stale
- **WHEN** a generated-owned artifact no longer matches the recorded digest or
  ChangeRail source identity
- **THEN** `verify-project` exits non-zero
- **AND** the output identifies the stale artifact and refresh remediation path

#### Scenario: Project-owned divergence is present
- **WHEN** a required wiring path is project-owned or missing generated
  ownership metadata under generated Windows policy
- **THEN** `verify-project` exits non-zero
- **AND** the output distinguishes project-owned divergence from stale
  generated-copy drift

### Requirement: Windows fallback proof verification
`verify-project` MUST fail closed when Windows symlink or junction fallback
policy lacks positive proof.

#### Scenario: Symlink fallback policy is declared
- **WHEN** verification inspects a native Windows consumer that declares
  symlink fallback wiring
- **THEN** it requires recorded positive Developer Mode or symlink privilege
  proof
- **AND** the proof MUST include schema-valid source metadata and concrete
  per-check evidence, not only passed status names
- **AND** missing or negative proof is a blocking failure

#### Scenario: Junction fallback policy is declared
- **WHEN** verification inspects a native Windows consumer that declares
  junction fallback wiring
- **THEN** it requires recorded link-aware cleanup and Git-safety proof
- **AND** the proof MUST include schema-valid source metadata and concrete
  per-check evidence, not only passed status names
- **AND** missing or negative proof is a blocking failure
