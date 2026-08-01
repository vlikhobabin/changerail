## ADDED Requirements

### Requirement: Retained evidence handoff
ChangeRail delivery methodology MUST allow verification claims to be backed by
retained ignored runtime evidence references while keeping raw output out of
tracked public payload.

#### Scenario: Delivery records retained evidence reference
- **WHEN** delivery records a verification command outcome in a card, task or
  manifest
- **THEN** the record may cite a retained evidence id or runtime evidence path
  alongside the command and observed outcome
- **AND** it does not copy raw command output into tracked files

#### Scenario: Reviewer audits retained evidence
- **WHEN** independent review audits a verification claim with retained evidence
- **THEN** the reviewer can use the evidence reference as backing for the claim
  and can flag missing or stale retained evidence as an evidence finding
