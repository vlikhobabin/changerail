# Authorize bounded review fingerprint payload

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- none

## Series Index
- none

## Source
- `investigate-bounded-review-fingerprint-payload`

## Summary
Publish the machine-readable bounded authorization produced by the fingerprint
payload investigation. The authorization binds one exact successor, retains
the existing 500 production-LOC maximum and does not permit a new authority or
wire protocol.

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
- `investigate-bounded-review-fingerprint-payload`

## Authorization
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/investigate-bounded-review-fingerprint-payload.md","investigation_id":"investigate-bounded-review-fingerprint-payload","successor_card":"openspec/board/3.inprogress/deliver-bounded-review-fingerprint-optimization.md","successor_id":"deliver-bounded-review-fingerprint-optimization","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":false}`

## Acceptance
- The published `4.done` card contains exactly one schema-valid investigation
  authorization object bound to the investigation and successor card ids and
  canonical board paths.
- `production_loc_ceiling` is 500 and
  `allow_new_authority_or_wire_protocol` is false.
- The card depends on the completed investigation and introduces no production
  code or global review-policy relaxation.
- Focused preflight proves the authorization is consumable only by the exact
  successor after reciprocal relation checks pass.

## Change Set
- `authorize-bounded-review-fingerprint-payload`

## Verify
- `./bin/openspec validate "authorize-bounded-review-fingerprint-payload" --strict` - passed
- `./bin/openspec validate "changerail-contracts" --strict` - passed
- `python3 scripts/smoke-review-preflight.py` - passed; exact successor
  acceptance and mismatched-card rejection covered
- `./bin/openspec archive "authorize-bounded-review-fingerprint-payload" --yes --skip-specs` - passed
- `./bin/openspec validate --all --strict` - passed, 33 items after archive
- `python3 scripts/public-surface-scan.py` - passed, 1048 files scanned, 0 findings
- `./bin/changerail-delivery-manifest scope-check .runtime/changerail/delivery-manifests/authorize-bounded-review-fingerprint-payload.json --workspace . --target working-tree --json` - passed
- `git diff --check` - passed

## Archive
- `openspec/changes/archive/2026-08-19-authorize-bounded-review-fingerprint-payload/`

## Related
- `openspec/changes/authorize-bounded-review-fingerprint-payload/`
- `openspec/changes/archive/2026-08-19-authorize-bounded-review-fingerprint-payload/`
- `openspec/board/4.done/investigate-bounded-review-fingerprint-payload.md`
- `openspec/board/2.todo/deliver-bounded-review-fingerprint-optimization.md`

## Result
published; bounded review-fingerprint authorization source complete

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-bounded-review-fingerprint-payload`

### Why
The bounded review-fingerprint successor already declares a reference to a
published authorization source, but the source card is not yet a completed
tracked `4.done` artifact and therefore cannot be consumed by deterministic
preflight.

### Goal
Publish one schema-valid authorization object that binds the completed
investigation to the exact successor while keeping the ceiling at 500 added
production LOC and forbidding any new authority or wire protocol.

### Scope
- Complete the authorization card as the published source for successor
  `deliver-bounded-review-fingerprint-optimization`.
- Preserve the exact authorization payload fields:
  `investigation_card`, `investigation_id`, `successor_card`, `successor_id`,
  `production_loc_ceiling` and `allow_new_authority_or_wire_protocol`.
- Require reciprocal relation checks across the published investigation,
  authorization source and successor cards.
- Add or reuse focused deterministic preflight smoke evidence that proves exact
  successor acceptance and mismatched-card rejection.
- Do not implement the review-fingerprint optimization or raise global review
  complexity limits.

### Acceptance
- The completed authorization card contains exactly one schema-valid
  investigation authorization object.
- The object binds
  `openspec/board/4.done/investigate-bounded-review-fingerprint-payload.md` to
  `openspec/board/3.inprogress/deliver-bounded-review-fingerprint-optimization.md`
  with ids `investigate-bounded-review-fingerprint-payload` and
  `deliver-bounded-review-fingerprint-optimization`.
- `production_loc_ceiling` remains 500 and
  `allow_new_authority_or_wire_protocol` remains false.
- Focused preflight evidence proves the authorization can be consumed only by
  the exact successor after reciprocal relation checks.
- The payload introduces no production implementation and no global policy
  relaxation.

### Depends On
- `investigate-bounded-review-fingerprint-payload`

### Related
- `openspec/changes/authorize-bounded-review-fingerprint-payload/`

## Log
- 2026-08-19T07:17:52Z created as the bounded authorization publication step.
- 2026-08-19T07:51:09Z `$chrl-ff` created
  `authorize-bounded-review-fingerprint-payload`, recorded the bounded
  authorization publication plan and moved the card to `2.todo`.
- 2026-08-19T08:23:15Z `$chrl-do` synced the bounded authorization requirement,
  added focused exact-chain preflight smoke coverage and archived
  `authorize-bounded-review-fingerprint-payload`.
- 2026-08-19T08:23:51Z `$chrl-do` refreshed the delivery manifest and confirmed
  working-tree scope reconciliation for review handoff.
- 2026-08-19T08:43:40Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
