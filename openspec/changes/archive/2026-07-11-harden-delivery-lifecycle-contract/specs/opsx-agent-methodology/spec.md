## ADDED Requirements

### Requirement: Review-gated story finalization
OPSX MUST treat archived card-owned OpenSpec changes as completed change
payload, but MUST keep a review-gated story in `3.inprogress` until a fresh
`go` verdict is published.

#### Scenario: Delivery archives changes before review
- **WHEN** `opsx-do` finishes every planned change for a board card
- **THEN** the card-owned changes are archived and the card remains eligible for
  independent review while still in `3.inprogress`

#### Scenario: Publish finalizes the story
- **WHEN** `opsx-pub` successfully publishes a reviewed card payload
- **THEN** the card is finalized into `4.done` using the board's documented
  post-publish metadata protocol

### Requirement: Post-review change invalidation
OPSX MUST require re-review when any substantive tracked content, docs, specs,
schemas, scripts or tests change after a `go` verdict.

#### Scenario: Content changes after go
- **WHEN** a `go` verdict exists and a substantive file in the reviewed payload
  changes before publish
- **THEN** publish treats the verdict as stale and requires a fresh review

#### Scenario: Deterministic post-publish metadata
- **WHEN** publish records deterministic card metadata such as commit or push
  status after a successful commit
- **THEN** that metadata is separated from substantive reviewed payload changes
