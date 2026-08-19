## Why

The bounded review-fingerprint successor cannot use its already declared
published-investigation authorization until the authorization source itself is
a tracked, completed card with a schema-valid machine-readable payload. This
change publishes that narrow authorization without raising ChangeRail's global
review complexity limits.

## What Changes

- Move the authorization story through delivery as a documentation/contract
  payload that publishes exactly one investigation authorization object.
- Bind the authorization to the completed investigation
  `investigate-bounded-review-fingerprint-payload` and exact successor
  `deliver-bounded-review-fingerprint-optimization`.
- Preserve the existing maximum bounded ceiling of 500 added production LOC and
  keep `allow_new_authority_or_wire_protocol` set to false.
- Require focused deterministic preflight coverage that proves the authorization
  is consumable only by the exact successor after reciprocal relation checks.
- Avoid production-code changes, global review-policy relaxation, new authority
  and new wire protocol.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-contracts`: deterministic review preflight has one published
  review-fingerprint authorization source to validate against exact
  investigation, authorization and successor card identities.

## Impact

- Affected tracked files: this board card and
  `openspec/changes/authorize-bounded-review-fingerprint-payload/`.
- Expected delivery payload is board/OpenSpec documentation plus focused smoke
  assertions if existing coverage does not already prove the exact binding.
- Public-surface impact stays generic and contains no private repositories,
  credentials, runtime traces or retained source payloads.
