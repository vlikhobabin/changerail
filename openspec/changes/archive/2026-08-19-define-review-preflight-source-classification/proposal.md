## Why

The review preflight needs a deterministic way for consumer repositories to
declare which paths are production source for domain-specific formats without
hard-coding application names into ChangeRail core. Without that declaration,
BSL and Designer XML cannot be counted fail-closed without either false
negatives or broad XML false positives.

## What Changes

- Add a tracked, public-safe consumer source-classification contract for review
  preflight.
- Let consumers declare production roots and source-kind rules for specific
  path/suffix families while preserving ChangeRail's existing generic
  non-production exclusions.
- Extend the preflight result contract so complexity output can explain source
  kinds and counted measures instead of only one aggregate LOC number.
- Document the declaration in contract docs and bootstrap/project guidance
  without adding any 1C configuration names to generic ChangeRail core.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-contracts`: review preflight gains a schema-backed source
  classification input and source-kind breakdown output.
- `changerail-project-templates`: consumer bootstrap guidance exposes the
  optional source-classification file and keeps it project-owned.

## Impact

Affected files include `scripts/changerail_review_preflight.py`,
`schemas/changerail-review-preflight-result.schema.json`, a new source
classification schema if implementation chooses a separate schema file,
contract docs, project templates and focused smoke coverage. Consumer impact is
opt-in: repositories without the classification file keep existing generic
suffix and non-production behavior.
