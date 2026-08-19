# Support runner resume after investigation-required

## Status
1.backlog

## Owner
ChangeRail maintainer

## OpenSpec Stage
story

## Series
- none

## Series Index
- none

## Source
- Field validation of a package-runner delivery stopped by deterministic review
  complexity preflight.
- `bin/changerail-delivery-runner`

## Summary
The delivery runner correctly returns `BLOCKED: investigation_required` after
an implementation child retains an unreviewed dirty payload. Current
single-card `resume` accepts only remote publish-target failures, while a fresh
`run` or `run-plan` requires a clean workspace. The operator therefore cannot
resume the retained exact payload through the package runner after publishing
the required investigation and bounded authorization.

Add a fail-closed recovery contract for an `investigation_required` child that
preserves exact payload identity, requires the published reciprocal
authorization chain, and resumes review/publish without treating an unreviewed
checkpoint commit as review evidence.

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `yes`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Acceptance
- Runner records enough schema-backed retained-payload identity at the
  `investigation_required` stop to reject unrelated or mutated work on resume.
- An explicit resume path accepts only the prior matching card/workspace/status
  and re-runs deterministic preflight after the investigation and authorization
  sources are clean tracked `HEAD` artifacts.
- Resume preserves the unreviewed payload as a working-tree review target; it
  does not accept a WIP commit, stash name, branch name or prose assertion as a
  substitute for exact fingerprint proof.
- Queue resume can represent the authorized recovery and keeps downstream cards
  blocked until the original or replacement payload is independently reviewed
  and published.
- Stale, missing, over-ceiling, relation-mismatched or payload-drifted recovery
  remains `BLOCKED` with a stable machine reason.
- Focused synthetic smokes cover successful recovery and adversarial dirty,
  stale authorization, wrong card, wrong workspace and fingerprint drift cases.

## Non-Goals
- Automatically authorizing a large payload.
- Relaxing clean-tree requirements for ordinary initial runner launches.
- Reading or publishing raw child logs as recovery proof.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `openspec/specs/changerail-delivery-runner/spec.md`

## Result
not started

## Next
- triage after the current bounded replacement is delivered

## Log
- 2026-08-19T07:17:52Z created after package-runner delivery could not resume a
  retained `investigation_required` payload through either `resume` or a fresh
  clean-tree launch.
