## ADDED Requirements

### Requirement: Delivery manifest publish ledger
Delivery manifests MUST distinguish the reviewed payload commit from the final
published commit and MUST record final push metadata in ignored runtime state.

#### Scenario: Publish records payload and published commits
- **WHEN** `changerail-pub` commits a reviewed payload, finalizes the board card,
  amends deterministic card metadata and publishes the result
- **THEN** the delivery manifest records the original payload commit as
  `publish.payload_commit`
- **AND** it records the final pushed commit as `publish.published_commit`
- **AND** it records final remote, branch, status and push timestamp in
  `publish`

#### Scenario: Publish updates card location in manifest
- **WHEN** helper-assisted finalization moves a board card from `3.inprogress`
  to `4.done`
- **THEN** the ignored delivery manifest records the final `card.path`
- **AND** it records the final `card.status`

#### Scenario: Local-only publish records skipped push
- **WHEN** publish runs with explicit `--no-push`
- **THEN** the delivery manifest records the final committed payload state
- **AND** it records `publish.status: skipped` with a reason and local-only mode
  instead of claiming remote publication readiness

#### Scenario: Manifest validates publish ledger fields
- **WHEN** the delivery manifest helper validates a manifest containing publish
  ledger metadata
- **THEN** schema-backed validation accepts non-empty `payload_commit`,
  `published_commit`, remote, branch, status and timestamp fields
- **AND** validation fails for `publish.status: pushed` unless
  `payload_commit`, `published_commit`, remote, branch, pushed timestamp and
  status are present
- **AND** it rejects unknown publish fields or malformed date-time values

#### Scenario: Manifest validates local-only skipped publish evidence
- **WHEN** the delivery manifest helper validates a manifest with
  `publish.status: skipped`
- **THEN** validation fails unless `payload_commit`, `published_commit`,
  `reason` and `mode: local-only` are present
