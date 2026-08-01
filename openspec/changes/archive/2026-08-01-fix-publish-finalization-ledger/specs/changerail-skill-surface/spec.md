## MODIFIED Requirements

### Requirement: Publish finalizes board metadata deterministically
`changerail-pub` MUST define deterministic board finalization behavior for
review-gated cards after the reviewed payload commit succeeds, while keeping
tracked card metadata stable and storing exact mutable publication details in
ignored runtime manifest evidence.

#### Scenario: Publish commits reviewed payload
- **WHEN** `changerail-pub` commits a reviewed card payload
- **THEN** it finalizes the board card into `4.done`, records stable completion
  metadata, and amends only card metadata when required by board protocol
- **AND** it does not make substantive code, docs, specs, schema, script or
  test edits after the fresh `go` verdict
- **AND** it does not write the card's own exact final commit hash or mutable
  push status into tracked done-card text
- **AND** it records payload commit, final published commit, remote, branch,
  status and timestamps in the ignored delivery manifest when available
