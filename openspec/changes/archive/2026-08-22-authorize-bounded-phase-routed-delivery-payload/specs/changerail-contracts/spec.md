## ADDED Requirements

### Requirement: Published bounded phase-routed delivery authorization source
ChangeRail MUST publish the bounded phase-routed delivery authorization as one
clean tracked `4.done` board card before successor
`implement-phase-routed-delivery-authorization-boundary` can use the bounded
production-LOC and aggregate/child authority, resume and status
protocol-boundary exception. The source MUST contain exactly one schema-valid
investigation authorization object with only the six generic authorization
fields, bound to investigation
`investigate-phase-routed-delivery-authorization-boundary`, successor
`implement-phase-routed-delivery-authorization-boundary`, production LOC
ceiling 500 and `allow_new_authority_or_wire_protocol` true.

#### Scenario: Exact phase-routed successor consumes the authorization
- **WHEN** deterministic review preflight evaluates
  `implement-phase-routed-delivery-authorization-boundary` in `3.inprogress`
  after the investigation and authorization cards are published in `4.done`
- **THEN** it accepts the bounded authorization only if the successor references
  `openspec/board/4.done/authorize-bounded-phase-routed-delivery-payload.md`
- **AND** the authorization source depends on
  `investigate-phase-routed-delivery-authorization-boundary`
- **AND** the published investigation blocks
  `implement-phase-routed-delivery-authorization-boundary`
- **AND** the successor depends on
  `investigate-phase-routed-delivery-authorization-boundary` and references
  the authorization source
- **AND** the authorization object uses the exact investigation id, successor
  id, canonical board paths, ceiling 500 and protocol allowance true

#### Scenario: Phase-routed authorization mismatch fails closed
- **WHEN** another card references the source or any card id, canonical path,
  investigation relation, ceiling or protocol flag differs from the published
  authorization chain
- **THEN** deterministic review preflight returns `investigation-required`
- **AND** it does not launch semantic review or treat the source as authority
  for a third repair, an alternate aggregate runtime root, a reusable protocol
  waiver or weakened global review policy
