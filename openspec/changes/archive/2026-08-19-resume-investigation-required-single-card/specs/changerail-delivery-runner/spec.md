## ADDED Requirements

### Requirement: Explicit single-card resume after investigation required
The delivery runner MUST provide an explicit single-card resume path that
accepts a prior `changerail.delivery-run.v1` status only when it belongs to the
same card and workspace, has `terminal_outcome: BLOCKED`,
`terminal_reason: investigation_required`, and contains matching
retained-payload identity.

#### Scenario: Resume succeeds after published authorization
- **WHEN** prior single-card status stopped at `investigation_required`
- **AND** its retained-payload identity matches the current workspace and card
- **AND** the published investigation and bounded authorization sources are
  tracked, clean at `HEAD` and relation-matched to the current card
- **THEN** single-card `resume --status-path <status.json>` continues to the
  review/publish portion for the retained working-tree payload
- **AND** the resumed status records fresh deterministic preflight evidence

#### Scenario: Resume rejects mismatched status identity
- **WHEN** prior status is missing, schema-invalid, stale, belongs to another
  card or belongs to another workspace
- **THEN** single-card resume records `BLOCKED`
- **AND** it exits non-zero before launching a child continuation
- **AND** it records a stable machine reason for the mismatch

#### Scenario: Resume rejects payload drift
- **WHEN** the prior status contains retained-payload identity
- **AND** the current `HEAD`, reviewed tree SHA or diff fingerprint differs from
  that identity outside the clean tracked authorization sources
- **THEN** single-card resume records `BLOCKED`
- **AND** it does not treat the current working tree as the retained review
  target

### Requirement: Retained resume does not trust checkpoint commits
Single-card retained-payload resume MUST preserve the dirty working tree as the
review target and MUST NOT treat a WIP commit, stash name, branch name or prose
assertion as a substitute for retained-payload fingerprint proof.

#### Scenario: Checkpoint commit is not review evidence
- **WHEN** an operator provides a commit or branch that contains the unreviewed
  payload but the prior retained-payload fingerprint does not match the current
  working tree
- **THEN** resume remains `BLOCKED`
- **AND** the runner does not use that commit or branch as independent review
  evidence

#### Scenario: Ordinary launch remains clean-tree gated
- **WHEN** the operator starts `run`, `run-plan` or a remote-preflight resume
  without a valid prior `investigation_required` retained-payload status
- **THEN** the existing clean-workspace launch requirements remain in force
