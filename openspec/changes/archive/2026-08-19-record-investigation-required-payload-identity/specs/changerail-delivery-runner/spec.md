## ADDED Requirements

### Requirement: Investigation-required retained payload identity
The delivery runner MUST record schema-valid retained-payload identity when a
single-card delivery child stops with `terminal_outcome: BLOCKED`,
`terminal_reason: investigation_required`, and leaves an unreviewed working-tree
payload for possible recovery.

#### Scenario: Runner records retained identity at safety stop
- **WHEN** a delivery child reports `BLOCKED` with
  `terminal_reason: investigation_required`
- **AND** the workspace still contains the unreviewed payload that triggered
  deterministic review preflight
- **THEN** the runner status includes a `retained_payload` object
- **AND** that object identifies the source run, card, workspace, `HEAD`
  commit, reviewed tree SHA, diff fingerprint and working-tree review target

#### Scenario: Identity capture failure remains blocked
- **WHEN** the runner cannot compute a canonical retained-payload fingerprint
  after an `investigation_required` stop
- **THEN** the runner keeps the terminal outcome `BLOCKED`
- **AND** it records a stable machine diagnostic for missing retained-payload
  identity instead of silently accepting an unverifiable resume target

### Requirement: Retained identity excludes raw payload evidence
The delivery runner MUST keep retained-payload identity bounded to metadata and
MUST NOT copy raw source payload, raw child stdout/stderr, secrets or ignored
runtime evidence into tracked files as proof for a later resume.

#### Scenario: Raw logs are not retained as identity
- **WHEN** the runner records retained-payload identity for an
  `investigation_required` stop
- **THEN** the identity contains fingerprint and path metadata only
- **AND** raw child logs remain referenced through ignored runtime paths rather
  than embedded in card, schema or OpenSpec artifacts

#### Scenario: WIP references are not identity proof
- **WHEN** a blocked status names a WIP commit, stash, branch name or prose
  assertion but lacks the schema-valid retained-payload fingerprint
- **THEN** ChangeRail does not treat that reference as retained-payload identity
