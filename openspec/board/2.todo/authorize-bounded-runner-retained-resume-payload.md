# Authorize bounded runner retained resume payload

## Status
2.todo

## Owner
ChangeRail maintainer

## OpenSpec Stage
story

## Series
- none

## Series Index
- none

## Source
- `investigate-runner-retained-resume-payload-boundary`

## Summary
Publish the machine-readable bounded authorization produced by the retained
runner-resume investigation. The authorization binds one exact successor,
keeps the existing 500 production-LOC maximum and permits only the runner/status
protocol boundary already accepted by the investigation decision.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Depends On
- `investigate-runner-retained-resume-payload-boundary`

## Authorization
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/investigate-runner-retained-resume-payload-boundary.md","investigation_id":"investigate-runner-retained-resume-payload-boundary","successor_card":"openspec/board/3.inprogress/support-runner-resume-after-investigation-required.md","successor_id":"support-runner-resume-after-investigation-required","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- The published `4.done` card contains exactly one schema-valid investigation
  authorization object bound to the completed investigation and exact
  successor ids and canonical board paths.
- `production_loc_ceiling` is 500 and
  `allow_new_authority_or_wire_protocol` is true only for the retained-resume
  runner/status boundary accepted by the investigation.
- The card depends on the completed investigation and introduces no production
  code or global review-policy relaxation.
- Focused deterministic preflight proves the authorization is consumable only
  by the exact successor after reciprocal relation checks pass.

## Non-Goals
- Implementing or publishing the retained runner-resume payload.
- Raising the global complexity or bounded-authorization ceilings.
- Authorizing another card, workspace, authority boundary or wire protocol.

## Change Set
- `authorize-bounded-runner-retained-resume-payload`

## Verify
- not started

## Archive
- not started

## Related
- `openspec/board/4.done/investigate-runner-retained-resume-payload-boundary.md`
- `openspec/board/2.todo/support-runner-resume-after-investigation-required.md`
- `scripts/smoke-review-preflight.py`
- `openspec/specs/changerail-contracts/spec.md`

## Result
not started

## Next
- `$changerail-deliver openspec/board/2.todo/authorize-bounded-runner-retained-resume-payload.md`

## Change 1: `authorize-bounded-runner-retained-resume-payload`

### Why
The published investigation selected the existing runner-resume successor but
cannot itself authorize the critical new-wire payload. Deterministic preflight
requires a separate completed authorization source bound to the exact
successor and bounded at 500 production-counted LOC.

### Goal
Publish one schema-valid authorization object for the exact bounded successor
without changing production runner behavior or global review policy.

### Scope
- Complete the authorization card as the published source for successor
  `support-runner-resume-after-investigation-required`.
- Preserve the exact investigation, successor, canonical path, ceiling and
  protocol-permission fields.
- Require reciprocal relation checks across the investigation, authorization
  source and successor cards.
- Add or reuse focused deterministic preflight smoke evidence for exact
  successor acceptance and mismatched-card rejection.

### Acceptance
- The completed card contains exactly one schema-valid authorization object.
- The object binds the completed investigation to the future in-progress path
  of the exact successor with a ceiling of 500 production-counted LOC.
- The authorization permits the accepted runner/status protocol boundary but
  no broader authority.
- Focused preflight evidence proves exact-chain acceptance and mismatch
  rejection.

### Depends On
- none

### Related
- `openspec/changes/authorize-bounded-runner-retained-resume-payload/`

## Log
- 2026-08-19T17:36:05Z created after the published investigation selected a
  simplified same-card successor bounded at 500 production-counted LOC.
