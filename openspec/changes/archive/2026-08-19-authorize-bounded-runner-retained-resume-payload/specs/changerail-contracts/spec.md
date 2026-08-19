## ADDED Requirements

### Requirement: Published bounded runner retained-resume authorization source
ChangeRail MUST publish the bounded runner retained-resume authorization as one
clean tracked `4.done` board card before successor
`support-runner-resume-after-investigation-required` can use the bounded
production-LOC and runner/status protocol-boundary exception. The authorization
source MUST contain exactly one schema-valid investigation authorization object
bound to investigation `investigate-runner-retained-resume-payload-boundary`,
successor `support-runner-resume-after-investigation-required`, production LOC
ceiling 500 and `allow_new_authority_or_wire_protocol` true.

#### Scenario: Authorization source binds the exact runner resume card chain
- **WHEN** deterministic review preflight evaluates
  `support-runner-resume-after-investigation-required` after the investigation
  and authorization cards are published in `4.done`
- **THEN** it accepts the bounded authorization only if the successor references
  `openspec/board/4.done/authorize-bounded-runner-retained-resume-payload.md`
- **AND** the authorization source depends on
  `investigate-runner-retained-resume-payload-boundary`
- **AND** the published investigation blocks
  `support-runner-resume-after-investigation-required`
- **AND** the authorization object uses the exact investigation id, successor
  id, canonical board paths, ceiling 500 and protocol allowance true

#### Scenario: Runner resume authorization cannot be reused
- **WHEN** another card references the published runner retained-resume
  authorization source or the exact reciprocal card links do not match
- **THEN** deterministic review preflight returns `investigation-required`
- **AND** it does not launch an LLM review or treat the authorization as a
  reusable waiver
