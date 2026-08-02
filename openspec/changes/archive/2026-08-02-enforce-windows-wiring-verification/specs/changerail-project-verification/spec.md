## ADDED Requirements

### Requirement: Generated Windows wiring verification smoke matrix
ChangeRail MUST provide deterministic smoke coverage proving that
`verify-project` accepts only fresh generated Windows wiring and fails closed on
stale, missing or project-owned generated artifacts.

#### Scenario: Fresh generated wiring passes
- **WHEN** `python3 scripts/smoke-verify-project.py` creates a generated
  Windows consumer fixture
- **THEN** `bin/verify-project <path> --json` reports passing checks for the
  generated wiring manifest and representative generated file and directory
  artifacts

#### Scenario: Missing generated artifact fails
- **WHEN** a manifest-owned generated artifact is absent from the consumer
  fixture
- **THEN** `bin/verify-project <path> --json` exits non-zero
- **AND** the failed check identifies the missing generated artifact

#### Scenario: Stale generated artifact fails with remediation
- **WHEN** a generated-owned artifact no longer matches the current ChangeRail
  source digest
- **THEN** `bin/verify-project <path> --json` exits non-zero
- **AND** the failed check identifies stale generated wiring and the
  `--refresh-wiring` remediation path

#### Scenario: Project-owned divergence remains blocking
- **WHEN** generated wiring content diverges without matching manifest-owned
  generated state
- **THEN** `bin/verify-project <path> --json` exits non-zero
- **AND** the failed check distinguishes project-owned divergence from stale
  generated-copy drift
