## Context

The public schema set already includes
`changerail-maintenance-quality-rollup.schema.json` and
`changerail-maintenance-proposal-decision.schema.json`, and schema smoke covers
them. `bin/verify-project` still requires only the earlier maintenance schemas
for opted-in consumers, so missing quality/proposal contracts do not block
consumer verification.

## Goals / Non-Goals

**Goals:**
- Make the opted-in maintenance schema inventory in `verify-project` match the
  tracked public maintenance schema inventory.
- Prove missing/stale contract failures in focused smoke coverage.
- Preserve no-scan verifier behavior.

**Non-Goals:**
- Change schema ids or schema shapes.
- Add full maintenance scan execution to `verify-project`.
- Change opt-out behavior for consumers without maintenance artifacts.

## Decisions

1. Extend the existing `MAINTENANCE_SCHEMAS` inventory in `bin/verify-project`.
   This keeps schema reachability checks in the same code path as the earlier
   maintenance contracts and avoids a parallel special case for quality.

2. Update smoke expectations and negative fixtures instead of adding broad
   release-only checks. Focused verifier smoke should prove that opted-in
   consumers fail closed when either new schema is unreachable or stale under a
   generated-copy ownership model.

3. Keep verification limited to wiring/contracts. Full maintenance scan behavior
   remains owned by dedicated first-run and repository-knowledge smokes.

## Risks / Trade-offs

- [Risk] Existing opted-in consumers with old ChangeRail source checkouts will
  start failing verification. Mitigation: this is intentional fail-closed
  behavior for incomplete public contract wiring and diagnostics should name the
  missing schema.
- [Risk] Generated-copy schema freshness may be confused with helper freshness.
  Mitigation: smoke should keep stale helper and missing schema fixtures
  distinct.
