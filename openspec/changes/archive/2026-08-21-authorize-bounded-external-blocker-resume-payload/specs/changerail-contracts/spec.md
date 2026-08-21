## ADDED Requirements

### Requirement: External-resume authorization MUST bind exact successor
ChangeRail MUST принимать external-blocker retained-resume authorization только
для exact `resume-retained-payload-after-external-blocker` successor in
`3.inprogress`, bound к published batch investigation, ceiling 500 и protocol
allowance true.

#### Scenario: Exact external-resume chain
- **WHEN** reciprocal ids/paths совпадают и payload внутри ceiling
- **THEN** protocol/LOC complexity stop может быть снят
- **AND** critical semantic review остается обязательным

#### Scenario: Generic dirty authority запрошена
- **WHEN** другой successor или broader credential/target authority ссылается
  на source
- **THEN** authorization отклоняется
