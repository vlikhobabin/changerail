## ADDED Requirements

### Requirement: Supported live progress view
ChangeRail status readers MUST показывать latest validated child progress,
heartbeat timestamp и bounded health через single-card и aggregate views, не
требуя от оператора чтения raw JSONL или stderr logs.

#### Scenario: Оператор опрашивает long-running card
- **WHEN** оператор читает single-card или plan status active delivery
- **THEN** view показывает latest generic phase/stage, heartbeat и health для
  этой карточки
- **AND** не отображает prompts, command text, output excerpts или environment
  values

#### Scenario: Aggregate child identity не совпадает
- **WHEN** plan видит child status, run/card identity которого не совпадает с
  active plan entry
- **THEN** aggregate status не mirror его progress
- **AND** вместо этого выдает bounded invalid-child diagnostic
