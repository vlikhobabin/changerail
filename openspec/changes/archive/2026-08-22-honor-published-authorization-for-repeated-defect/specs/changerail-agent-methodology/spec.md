## MODIFIED Requirements

### Requirement: Rescue complexity guard
ChangeRail MUST stop patch-staircase rescue for investigation and simplification
when bounded complexity signals are crossed. The default stop is more than 300
production LOC, a new authority or wire protocol, or a repeated defect class.
A successor may cross one of these signals only through a valid structured
published authorization source that binds its exact published investigation
and required card links; production LOC remains capped by the source at no more
than 500 and protocol remains controlled by its explicit boolean allowance.
Missing, stale, mismatched, disallowed or over-ceiling authorization MUST still
require investigation.

#### Scenario: Rescue crosses a complexity signal
- **WHEN** a rescue adds more than 300 production LOC, introduces a new authority
  or wire protocol, or repeats the same defect class without valid published
  investigation authorization
- **THEN** preflight returns `investigation-required`
- **AND** implementation rescue does not continue on the same patch staircase

#### Scenario: Published investigation authorizes a bounded successor
- **WHEN** a published authorization source has an exact investigation/successor
  binding and that successor references it while remaining within its LOC
  ceiling and protocol allowance
- **THEN** preflight permits only the declared bounded complexity exception,
  including an explicitly declared repeated defect
- **AND** the successor still receives its declared risk-appropriate payload
  review
