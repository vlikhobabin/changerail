## Why

Review, delivery and evidence handoffs need machine-readable contracts in the
OPSX namespace before projects can treat `/opt/opsx` as the public source of
truth. The review gate also needs a local helper for verdict validation and
working-tree freshness fingerprints.

## What Changes

- Add JSON schemas for `opsx.review-verdict.v1`,
  `opsx.delivery-manifest.v1` and `opsx.evidence-index.v1`.
- Add `scripts/opsx_review_verdict.py` and `bin/opsx-review-verdict`.
- Validate only the canonical `opsx.review-verdict.v1` schema id.
- Document the contract namespace and helper usage.

## Capabilities

### New Capabilities
- `opsx-contracts`: public wire contracts for review verdicts, delivery
  manifests and evidence indexes.

### Modified Capabilities
- none

## Impact

- Affected files: `schemas/**`, `scripts/opsx_review_verdict.py`,
  `bin/opsx-review-verdict`, `docs/opsx-contracts.md`, `README.md`,
  `docs/opsx-source-of-truth-architecture.md`, `openspec/specs/**`.
- Publish and review flows can validate contract artifacts through OPSX-local
  paths.
- Runtime verdicts and manifests remain ignored state and are not committed.
