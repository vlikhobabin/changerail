## ADDED Requirements

### Requirement: Queue observability records
ChangeRail delivery observability MUST treat aggregate queue status as a
structured metrics input alongside existing delivery run records and review
history.

#### Scenario: Queue status is available
- **WHEN** metrics read a `changerail.delivery-plan-status.v1` record
- **THEN** they can report queue result, card counts, child run references,
  terminal outcome and push/no-push mode without scraping raw logs

#### Scenario: Queue status is unavailable
- **WHEN** only existing child delivery run records are available
- **THEN** existing delivery metrics behavior remains compatible
- **AND** missing queue-level values are rendered as `unknown`
