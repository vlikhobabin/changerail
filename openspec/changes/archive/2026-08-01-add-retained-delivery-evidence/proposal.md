## Why

Review and publish gates can audit concise verification claims, but raw command
outputs are currently transient and lack a shared retained evidence contract.
That leaves reviewers unable to re-check important command outcomes without
re-running every check or trusting prose.

## What Changes

- Add a ChangeRail retained evidence contract for verification command captures
  under ignored runtime state.
- Extend the evidence index schema/helper surface so commands record identity,
  exit code, timestamps, concise summaries, raw output references and evidence
  classification.
- Allow delivery manifests and review verdicts to reference retained evidence
  without embedding raw logs in tracked payloads.
- Add focused smoke coverage for successful capture, failure capture, timeout,
  redaction and missing evidence.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-contracts`: defines retained evidence index semantics and helper
  behavior for ChangeRail-owned verification commands.
- `changerail-agent-methodology`: clarifies that retained runtime evidence may
  back verification claims without becoming tracked public payload.

## Impact

- `schemas/changerail-evidence-index.schema.json`
- `schemas/changerail-delivery-manifest.schema.json`
- `schemas/changerail-review-verdict.schema.json`
- `scripts/` and `bin/` helper surface for retained evidence capture
- `skills/` review/delivery references where evidence handoff is documented
- Focused smoke tests and release baseline coverage
