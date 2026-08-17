## MODIFIED Requirements

### Requirement: Board cards declare review risk
Generated and source board card templates MUST provide a concise review section
for risk and rescue-complexity declarations, including a
`Published investigation authorization` field whose default is `none`. The
field MUST document that any non-default value is one inline JSON object bound
to published investigation and successor cards; template prose MUST NOT imply
that arbitrary text authorizes a complexity exception.

#### Scenario: Agent creates a card from the template
- **WHEN** a new card is created from a ChangeRail board template
- **THEN** the card exposes risk tier, milestone audit, authority/protocol,
  credential/mutation-authority, repeated-defect, live-admission,
  final-certification and published-investigation authorization fields
- **AND** ordinary is the backward-compatible default risk
