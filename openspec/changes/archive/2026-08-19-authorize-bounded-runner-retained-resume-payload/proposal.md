## Why

The retained runner-resume successor cannot use the investigation decision until
there is a clean, tracked `4.done` authorization source that deterministic
review preflight can validate. This change publishes that narrow authorization
without implementing the retained-resume runner payload or changing global
review policy.

## What Changes

- Move the authorization story through delivery as a documentation/contract
  payload that publishes exactly one investigation authorization object.
- Bind the authorization to completed investigation
  `investigate-runner-retained-resume-payload-boundary` and exact successor
  `support-runner-resume-after-investigation-required`.
- Preserve the bounded production LOC ceiling of 500 and set
  `allow_new_authority_or_wire_protocol` to true only for the runner/status
  retained-resume boundary accepted by the investigation decision.
- Require focused deterministic preflight evidence that proves the
  authorization is consumable only by the exact successor after reciprocal
  relation checks.
- Avoid production-code changes, global review-policy relaxation, new
  credentials authority and retained-payload implementation work.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-contracts`: deterministic review preflight has one published
  runner retained-resume authorization source to validate against exact
  investigation, authorization and successor card identities.

## Impact

- Affected tracked files: this board card,
  `openspec/changes/authorize-bounded-runner-retained-resume-payload/` and the
  `changerail-contracts` spec after sync/archive.
- Expected delivery payload is board/OpenSpec documentation plus focused smoke
  assertions if existing coverage does not already prove the exact binding.
- Public-surface impact stays generic and contains no private repositories,
  credentials, runtime traces or retained source payloads.
