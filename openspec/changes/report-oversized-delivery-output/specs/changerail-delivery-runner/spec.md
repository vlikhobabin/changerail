## ADDED Requirements

### Requirement: Runner reports oversized command summary
The delivery runner MUST print a sanitized operator-facing summary of top
oversized commands when command output metadata exceeds the documented
threshold.

#### Scenario: Oversized commands exist
- **WHEN** a delivery run records commands whose output exceeds the threshold
- **THEN** runner terminal output identifies the top oversized commands with
  sanitized labels, byte counts and threshold information
- **AND** it provides remediation that points operators toward scoped paths,
  file-name discovery, counts or bounded excerpts

#### Scenario: Command label contains sensitive-looking material
- **WHEN** an oversized command label contains URL userinfo, token-like
  assignments or local runtime paths
- **THEN** the operator-facing summary redacts or omits those values before
  printing or writing structured summary fields

### Requirement: Oversized output smoke remains bounded
ChangeRail delivery runner smoke MUST prove that oversized command output is
accounted for without copying raw payloads into status records.

#### Scenario: Synthetic child emits oversized command output
- **WHEN** the delivery runner smoke launches a synthetic child that emits
  oversized command output
- **THEN** the runner status records byte accounting and threshold metadata
- **AND** the status record remains below the documented bounded size
- **AND** the raw oversized payload does not appear in `status.json`

#### Scenario: Raw evidence remains ignored
- **WHEN** the synthetic oversized output smoke retains raw stdout or stderr
  evidence
- **THEN** the evidence path remains under ignored runtime state
- **AND** delivery manifest or scoped publish helpers do not treat it as a
  committable path
