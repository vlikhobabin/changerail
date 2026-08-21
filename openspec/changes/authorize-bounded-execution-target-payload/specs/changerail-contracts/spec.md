## ADDED Requirements

### Requirement: Execution-target authorization MUST bind exact successor
ChangeRail MUST принимать bounded execution-target authorization только из
published source, bound к `investigate-bounded-field-validation-batch` и exact
successor `enforce-declared-execution-target-invariant` в `3.inprogress`, с
ceiling 500 и protocol allowance true.

#### Scenario: Exact successor consumes source
- **WHEN** reciprocal investigation/source/successor links и paths совпадают
- **THEN** deterministic preflight применяет ceiling 500 и protocol allowance

#### Scenario: Другой payload ссылается на source
- **WHEN** successor id/path или investigation relation не совпадает
- **THEN** authorization отклоняется как invalid
