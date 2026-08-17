## Why

The deterministic review preflight counts Go test files as production and cannot
validate the published investigation decision that bounds an approved successor
payload. The result is a false investigation stop and an unsafe temptation to
use an unstructured override.

## What Changes

- Exclude Go `*_test.go` files from production LOC accounting.
- Add one card-declared JSON reference to a published authorization source that
  binds exact investigation and successor identities, a ceiling up to 500 and
  an authority/wire protocol allowance.
- Fail closed to `investigation-required` for absent, stale, unreadable or
  mismatched authorization and for LOC over the declared ceiling.
- Document the concise declaration in the preflight contract and card templates.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-contracts`: preflight result and deterministic complexity guard
  expose and validate a published-investigation authorization.
- `changerail-agent-methodology`: bounded investigation authorization is the
  sole exception to the default complexity stop.
- `changerail-project-templates`: card templates expose the structured review
  declaration without granting an override by prose.

## Impact

`scripts/changerail_review_preflight.py`, its focused smoke, the preflight
schema, shared methodology, card templates and targeted public documentation.
No new service, model launcher, runtime host or free-form CLI override is added.
