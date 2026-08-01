## ADDED Requirements

### Requirement: Retained verification evidence capture
ChangeRail MUST provide a helper for ChangeRail-owned verification commands that
captures retained evidence with command identity, timestamps, exit code,
classification, concise summary and raw output reference.

#### Scenario: Successful verification command is retained
- **WHEN** the evidence helper runs a ChangeRail-owned verification command from
  an argv array and the command exits zero
- **THEN** it writes an evidence index entry with a stable evidence id, command
  argv summary, `started_at`, `ended_at`, exit code, classification and concise
  observed summary
- **AND** it writes the command output under ignored `.runtime/changerail/`
  evidence storage and records a repository-relative raw output path

#### Scenario: Failed verification command is retained
- **WHEN** the evidence helper runs a verification command that exits non-zero
- **THEN** it records the non-zero exit code and observed failure summary in the
  evidence index
- **AND** it exits non-zero for the caller without discarding the retained
  runtime evidence

#### Scenario: Timed-out verification command is retained
- **WHEN** the evidence helper terminates a command because its configured
  timeout elapsed
- **THEN** it records timeout status, elapsed timing and retained partial output
  evidence
- **AND** it exits non-zero for the caller

### Requirement: Runtime-only evidence storage
Retained raw command evidence MUST live only under ignored ChangeRail runtime
state, while tracked cards, manifests and verdicts may contain only concise
summaries and references.

#### Scenario: Evidence index uses ignored paths
- **WHEN** the evidence helper writes an index and raw output files
- **THEN** the paths are under `.runtime/changerail/evidence/`
- **AND** tracked card, manifest or verdict payloads contain references instead
  of raw command output

#### Scenario: Missing evidence is rejected
- **WHEN** evidence validation checks an index that references a missing runtime
  output file
- **THEN** validation exits non-zero with a structured diagnostic naming the
  missing evidence id or path

### Requirement: Evidence redaction safety
The evidence helper MUST avoid retaining obvious secret-like values from command
arguments or output.

#### Scenario: Secret-like argv is rejected before execution
- **WHEN** a requested command argv contains an obvious token-like assignment or
  credential-bearing value
- **THEN** the evidence helper refuses to execute the command
- **AND** it records a diagnostic without writing the secret-like value into the
  evidence index or raw output

#### Scenario: Secret-like output is redacted
- **WHEN** command output contains an obvious token-like assignment
- **THEN** the retained output replaces the sensitive value with a redaction
  marker
- **AND** the evidence index records that redaction occurred

### Requirement: Evidence classifications
Retained evidence entries MUST distinguish mandatory, diagnostic and
not-applicable verification evidence.

#### Scenario: Mandatory evidence is captured
- **WHEN** delivery captures a required verification command
- **THEN** the evidence entry classification is `mandatory`

#### Scenario: Diagnostic evidence is captured
- **WHEN** delivery captures a non-gating diagnostic command
- **THEN** the evidence entry classification is `diagnostic`

#### Scenario: Not-applicable evidence is recorded
- **WHEN** delivery records why RED evidence or another check is not applicable
- **THEN** the evidence entry classification is `not_applicable`
- **AND** the entry contains a concise reason instead of a raw command output

### Requirement: Evidence references in manifest and verdict contracts
Delivery manifests and review verdicts MUST allow concise evidence references
that identify retained evidence without embedding raw logs.

#### Scenario: Manifest references verification evidence
- **WHEN** delivery updates a manifest after running verification
- **THEN** `verification_summary` can include command evidence references with
  evidence id, index path and raw output path

#### Scenario: Review verdict references audited evidence
- **WHEN** a reviewer records acceptance or finding evidence
- **THEN** the review verdict can include evidence references with evidence id,
  index path and raw output path
- **AND** validation rejects malformed evidence reference objects

### Requirement: Retained evidence smoke coverage
ChangeRail smoke tests MUST cover retained evidence success, failure, timeout,
redaction and missing evidence cases.

#### Scenario: Evidence smoke suite runs
- **WHEN** the retained evidence smoke is executed
- **THEN** it observes helper success capture, non-zero capture, timeout
  capture, output redaction and missing evidence validation failure

#### Scenario: Release baseline includes evidence smoke
- **WHEN** the release baseline runs
- **THEN** retained evidence smoke coverage is included with the public contract
  and helper validation checks
