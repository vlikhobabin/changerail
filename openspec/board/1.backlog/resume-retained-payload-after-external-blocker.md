# Возобновление retained payload после внешнего blocker

## Status
1.backlog

## Owner
ChangeRail maintainers

## OpenSpec Stage
story

## Source
- Field validation of a supervised delivery stopped by a mandatory external
  platform verification gate.

## Summary
Single-card and package resume currently authorize an exact dirty retained
payload only when the prior terminal reason is `investigation_required`.
A delivery worker can also stop correctly after materializing implementation
when a mandatory external platform, service or credential gate is temporarily
unavailable. The resulting payload is preserved, but the runner offers no
machine-checkable resume path after the external condition is restored.

## Acceptance
- The runner models recoverable external blockers through a bounded structured
  contract rather than project-specific free-text terminal reasons.
- A blocked child can retain workspace, card, HEAD, tree and diff fingerprints
  without claiming successful delivery or bypassing review.
- Resume accepts a dirty workspace only when the prior status, blocker class,
  exact retained fingerprint and declared resume evidence all validate.
- Payload drift, another card/workspace, missing evidence or an unrecognized
  blocker fails closed before launching Codex.
- `resume-plan` can resume the original child and then continue its dependency
  queue; already delivered cards remain skipped.
- Tests cover successful recovery, stale evidence, payload drift, mixed
  workspaces, nonrecoverable blockers and compatibility with the existing
  investigation authorization path.

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
- `scripts/smoke-delivery-runner.py`

## Result
not started

## Next
- Explore the blocker taxonomy and evidence contract before moving to
  `2.todo`; do not broaden dirty-workspace authorization with a boolean bypass.

## Log
- 2026-08-20T07:55:00Z card created from a sanitized package-runner recovery
  finding.
- 2026-08-20T17:30:00Z the same delivery program required three manually
  launched recovery sessions. They preserved useful JSONL evidence but had no
  delivery-run status, parent attempt id, structured blocker transition or
  aggregate token/timing record. Promote recovery lineage and status parity to
  high priority; the retained-payload authorization model remains unchanged.
