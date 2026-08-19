## ADDED Requirements

### Requirement: Bounded runner retained-resume investigation decision
ChangeRail MUST publish a tracked investigation decision before the retained
runner-resume successor can use a bounded deterministic-preflight exception for
the prior oversized payload. The decision MUST reproduce the public-safe
preflight stop, bind the exact successor card, require a successor ceiling no
greater than 500 added production-counted LOC and preserve the retained-resume
verification floor.

#### Scenario: Investigation records retained runner preflight stop
- **WHEN** the investigation card is completed for the retained runner-resume
  payload
- **THEN** it records that deterministic preflight measured 562 added
  production-counted LOC in `bin/changerail-delivery-runner`
- **AND** it records that the retained payload declared a new runner/status
  protocol boundary without published investigation authorization
- **AND** it states that the retained payload is investigation input only and
  not reviewed or publishable evidence

#### Scenario: Successor remains exact runner resume card
- **WHEN** the investigation decision binds the successor
- **THEN** it names `support-runner-resume-after-investigation-required` as the
  exact successor id
- **AND** it records the current queue path
  `openspec/board/2.todo/support-runner-resume-after-investigation-required.md`
- **AND** it records the authorization-time target path
  `openspec/board/3.inprogress/support-runner-resume-after-investigation-required.md`
- **AND** it requires the later authorization source to use production LOC
  ceiling 500 and `allow_new_authority_or_wire_protocol` true
- **AND** it requires the successor and authorization source to retain exact
  reciprocal relations to the published investigation before deterministic
  preflight can consume the authorization

#### Scenario: Verification floor remains fail-closed
- **WHEN** the successor implementation is simplified below the bounded ceiling
- **THEN** it still verifies retained identity schema acceptance and rejection,
  single-card retained resume success, wrong card, wrong workspace, stale
  authorization, relation mismatch, over-ceiling authorization, fingerprint
  drift, queue original resume, queue replacement recovery and duplicate
  recovery rejection

#### Scenario: Over-ceiling successor cannot reuse the decision
- **WHEN** the successor still adds more than 500 production-counted LOC or
  changes to a different successor card without a new investigation decision
- **THEN** deterministic review preflight returns `investigation-required`
- **AND** it does not launch semantic review or treat this investigation as a
  reusable authorization waiver
