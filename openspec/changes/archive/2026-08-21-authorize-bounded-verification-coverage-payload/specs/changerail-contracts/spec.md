## ADDED Requirements

### Requirement: Verification-coverage authorization MUST bind exact successor
ChangeRail MUST принимать verification map/ledger protocol authorization только
для exact `define-verification-coverage-map` successor in `3.inprogress`, bound
к published batch investigation, ceiling 500 и protocol allowance true.

#### Scenario: Exact coverage chain
- **WHEN** reciprocal links совпадают и payload сохраняет investigated boundary
- **THEN** preflight применяет bounded exception

#### Scenario: Coverage becomes second acceptance source
- **WHEN** payload или другой successor расширяет source beyond references
- **THEN** authorization отклоняется
