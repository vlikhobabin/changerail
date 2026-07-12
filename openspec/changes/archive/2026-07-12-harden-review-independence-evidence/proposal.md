## Why

ChangeRail can validate that a verdict is fresh for a working tree, but the
current verdict helper does not validate any explicit independence attestation
from the reviewer. The contract needs to state the limit and require a
machine-checkable reviewer attestation.

## What Changes

- Add review independence attestation fields to the review verdict contract.
- Update the helper validation so missing or false independence attestations
  fail.
- Update review docs/skills to explain that the attestation is checked, while
  true session identity remains an operator/process guarantee.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-contracts`: review verdict schema and helper validation include
  reviewer independence attestation.
- `changerail-skill-surface`: review skill instructions require the reviewer to
  write the attestation and describe its limits.

## Impact

- Affected files: review verdict schema/helper/reference docs, review skill,
  contract docs/specs and focused smoke checks.
- Existing ignored runtime verdicts may need regeneration; tracked public
  artifacts should use the strengthened contract.
