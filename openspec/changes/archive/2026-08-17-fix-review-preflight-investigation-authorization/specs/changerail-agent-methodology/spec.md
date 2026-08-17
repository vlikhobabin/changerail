## MODIFIED Requirements

### Requirement: Rescue complexity guard
ChangeRail MUST stop patch-staircase rescue for investigation and simplification
when bounded complexity signals are crossed. The default stop is more than 300
production LOC, a new authority or wire protocol, or a repeated defect class.
A successor may exceed the default LOC ceiling up to an explicit maximum of 500
or declare a new authority/wire protocol only through a valid structured
published authorization source that binds its exact published investigation
and required card links. Missing, stale, mismatched or
over-ceiling authorization MUST still require investigation.

#### Scenario: Rescue crosses a complexity signal
- **WHEN** a rescue adds more than 300 production LOC, introduces a new authority
  or wire protocol, or repeats the same defect class without valid published
  investigation authorization
- **THEN** preflight returns `investigation-required`
- **AND** implementation rescue does not continue on the same patch staircase

#### Scenario: Published investigation authorizes a bounded successor
- **WHEN** a published investigation has an exact reciprocal successor binding
  and that successor declares a valid authorization up to 500 production LOC
  with the required protocol allowance
- **THEN** preflight permits only the declared bounded exception
- **AND** the successor still receives its declared risk-appropriate payload
  review
