## ADDED Requirements

### Requirement: Published bounded review-fingerprint authorization source
ChangeRail MUST publish the bounded review-fingerprint authorization as one
clean tracked `4.done` board card before the successor
`deliver-bounded-review-fingerprint-optimization` can use the bounded
production-LOC exception. The authorization source MUST contain exactly one
schema-valid investigation authorization object bound to investigation
`investigate-bounded-review-fingerprint-payload`, successor
`deliver-bounded-review-fingerprint-optimization`, production LOC ceiling 500
and `allow_new_authority_or_wire_protocol` false.

#### Scenario: Authorization source binds the exact card chain
- **WHEN** deterministic review preflight evaluates
  `deliver-bounded-review-fingerprint-optimization` after the investigation and
  authorization cards are published in `4.done`
- **THEN** it accepts the bounded authorization only if the successor references
  `openspec/board/4.done/authorize-bounded-review-fingerprint-payload.md`
- **AND** the authorization source depends on
  `investigate-bounded-review-fingerprint-payload`
- **AND** the published investigation blocks
  `deliver-bounded-review-fingerprint-optimization`
- **AND** the authorization object uses the exact investigation id, successor
  id, canonical board paths, ceiling 500 and protocol allowance false

#### Scenario: Mismatched authorization cannot be reused
- **WHEN** another card references the published review-fingerprint
  authorization source or the exact reciprocal card links do not match
- **THEN** deterministic review preflight returns `investigation-required`
- **AND** it does not launch an LLM review or treat the authorization as a
  reusable waiver
