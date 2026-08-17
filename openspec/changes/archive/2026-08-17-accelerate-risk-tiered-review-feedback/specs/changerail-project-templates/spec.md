## ADDED Requirements

### Requirement: Board cards declare review risk
Generated and source board card templates MUST provide a concise review section
for risk and rescue-complexity declarations.

#### Scenario: Agent creates a card from the template
- **WHEN** a new card is created from a ChangeRail board template
- **THEN** the card exposes risk tier, milestone audit, authority/protocol,
  credential/mutation-authority, repeated-defect, live-admission and
  final-certification fields
- **AND** ordinary is the backward-compatible default risk
