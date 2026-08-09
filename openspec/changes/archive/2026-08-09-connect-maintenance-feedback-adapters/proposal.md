## Why

Review-cycle history and blocked delivery-run records already contain structured
signals about recurring workflow issues, but repository maintenance currently
cannot normalize those signals into the existing finding lifecycle. This change
adds a schema-bound feedback path without scraping logs or changing frozen
review and delivery contracts.

## What Changes

- Add `bin/changerail-maintenance feedback` for explicit review-history,
  delivery-run and detector-result inputs.
- Normalize review findings into
  `changerail.maintenance-detector-result.v1` records while preserving source
  record reference, review cycle, original finding id, severity and safe
  affected relative paths.
- Normalize blocked delivery runs only when schema-valid records provide
  structured `BLOCKED` outcome and terminal reason.
- Reject malformed, unsafe, legacy prose-only or semantically incomplete inputs
  with schema-bound diagnostics.
- Reuse existing finding fingerprint, evidence and board dedup semantics.
- Preserve existing review, delivery, evidence and delivery-metrics schema ids
  and output columns.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-repository-knowledge`: repository maintenance accepts structured
  feedback evidence as read-only detector input and normalizes it through the
  existing finding lifecycle.

## Impact

- Affected public surfaces: `bin/changerail-maintenance`,
  `bin/changerail-maintenance.cmd`, `scripts/changerail_maintenance.py`,
  maintenance schemas and fixtures, repository-knowledge specs and smoke tests.
- Consumer projects can provide structured feedback through the existing
  detector adapter boundary; ChangeRail core does not parse consumer-specific
  retrospective prose and does not mutate external systems.
