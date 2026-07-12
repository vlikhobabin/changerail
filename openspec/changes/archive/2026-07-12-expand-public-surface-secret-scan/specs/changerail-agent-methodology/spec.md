## MODIFIED Requirements

### Requirement: Generic public-safe content
Public-safety verification MUST detect common secret assignments, private home
paths and reachable-history leaks while preserving generic examples.

#### Scenario: Public scanner detects secrets and home paths
- **WHEN** public-surface verification scans ChangeRail public files
- **THEN** it fails on token-like secret assignments and common Linux, macOS or
  Windows home-directory paths
- **AND** generic examples such as `/opt/changerail` and
  `/opt/example-project` remain allowed

#### Scenario: Scanner redacts secret values
- **WHEN** a token-like assignment is reported
- **THEN** scanner output identifies file, line and finding kind without
  printing the full secret value

#### Scenario: Scanner allows only explicit placeholder secrets
- **WHEN** public-surface verification encounters a token-like assignment
  containing words such as `token` or `secret`
- **THEN** it reports the assignment unless the value matches a narrow explicit
  placeholder allowlist

#### Scenario: Reachable history is scanned
- **WHEN** release verification runs the documented history scan mode
- **THEN** reachable git history is checked for the same public-safety finding
  classes without printing full secret values
