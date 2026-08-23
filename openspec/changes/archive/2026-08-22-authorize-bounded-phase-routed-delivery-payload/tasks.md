## 1. Publish Exact Authorization Source

- [x] 1.1 Preserve exactly one six-field authorization object on the source
  card with the published investigation id/path, exact successor id and
  `3.inprogress` path, ceiling 500 and protocol allowance true.
- [x] 1.2 Confirm the existing reciprocal contract: authorization source
  Depends On investigation, investigation Blocks exact successor, successor
  Depends On investigation and references the source; change the successor
  only if required to repair that metadata.
- [x] 1.3 Keep the successor queued until this source is published in `4.done`
  and keep production runner, schemas, CLI and runtime behavior unchanged.

## 2. Synchronize Contract And Preflight Coverage

- [x] 2.1 Sync the `changerail-contracts` delta requirement for this exact
  phase-routed authorization source without broadening the generic exception.
- [x] 2.2 Confirm `python3 scripts/smoke-review-preflight.py` proves exact
  phase-routed-chain acceptance and fail-closed rejection for changed card
  id/path, investigation relation, ceiling and protocol flag under that
  reciprocal contract; add only missing non-production coverage.
- [x] 2.3 Confirm the resulting scoped diff has zero production-counted LOC and
  does not authorize a third repair, alternate aggregate runtime root,
  reusable waiver or weakened global review policy.

## 3. Verify And Archive

- [x] 3.1 Run
  `bin/openspec validate authorize-bounded-phase-routed-delivery-payload --strict`.
- [x] 3.2 Run `bin/openspec validate changerail-contracts --strict` after spec
  synchronization.
- [x] 3.3 Run `python3 scripts/smoke-review-preflight.py`.
- [x] 3.4 Run `bin/openspec validate --all --strict`.
- [x] 3.5 Run `python3 scripts/public-surface-scan.py`.
- [x] 3.6 Run `git diff --check`, include new untracked artifacts in an explicit
  whitespace scan, and archive the completed change before review handoff.
