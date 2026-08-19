## Why

Designer XML exports can represent production metadata, but treating every
`.xml` file as production would make schemas, templates and fixtures false
positives and can make ordinary 1C delivery impossible under a raw line ceiling.
The preflight needs an explicit, bounded metric for declared production Designer
XML.

## What Changes

- Count Designer XML only when source classification proves it belongs to a
  declared production source kind.
- Add a structural XML complexity measure that is meaningful for hierarchical
  Designer exports and is separate from raw XML line count when needed.
- Extend the preflight result breakdown so BSL, Designer XML and mixed payloads
  show source kind, counted paths, raw added lines, effective complexity and
  guard reasons.
- Keep generic XML schemas, templates, fixtures and documentation out of
  production complexity by default.
- Preserve bounded investigation authorization: payloads above the default or
  authorized ceiling still stop fail-closed.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-contracts`: review preflight reports and enforces source-kind
  complexity for declared production Designer XML.

## Impact

Affected files include `scripts/changerail_review_preflight.py`,
`schemas/changerail-review-preflight-result.schema.json`,
`scripts/smoke-review-preflight.py`, contract docs and OpenSpec contract specs.
The implementation must use only synthetic temporary XML fixtures and must not
store real Designer exports in the public repository.
