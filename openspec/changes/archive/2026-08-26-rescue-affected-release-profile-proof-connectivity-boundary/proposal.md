# Proposal: proof-connectivity boundary для affected profile v4

## Why
The unpublished affected v3 implementation exhausted its only repair with two
counterfactual proof gaps. Continuing it would bypass review lifecycle and
would allow guard-removal or artifact-authority regressions to escape focused proof.

## What Changes
- Exhaust the unpublished v3 implementation without rewriting published history.
- Declare one exclusive docs-only authorization and clean v4 implementation path.
- Freeze a direct mutation oracle for every resolved-base validation guard.
- Freeze non-authoritative add/forge/replay fixtures for every forbidden protocol artifact.
- Preserve the closed v3 admission, selector, scheduler, authority and CI floor.

## Impact
- Methodology: terminal unpublished work is replaced through explicit lineage.
- Verification: v4 receives finite machine-checkable proof-connectivity boundaries.
- Public surface: docs/OpenSpec only; no code, dependency, schema or runtime state.
- Consumer projects: no impact.
