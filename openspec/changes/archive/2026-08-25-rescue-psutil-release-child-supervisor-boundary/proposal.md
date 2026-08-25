## Why

The published S v1 authorization binds exactly one successor and therefore
cannot authorize a psutil-backed replacement after the unpublished S v1
implementation exhausted its second cycle. An unpublished S2 authorization
attempt also failed its prerequisite; both episodes are forensic-only and need
a new published decision before any replacement authorization can exist.

## What Changes

- Add one docs-only release-CI decision for a future psutil-backed child
  supervisor S2, including its exact future authorization object and reciprocal
  dependency contract.
- Define the narrow future S2 supervision boundary: `psutil==7.1.0` pins,
  bounded stdlib `selectors`/`prctl` adapter, cgroup-independent containment,
  fail-closed psutil handling, identity-safe recursive cleanup and explicit
  timeout/cap limits.
- Keep S2 structurally dormant and require a later refresh after publication
  before downstream H4/I3/W1/R3/A3 authorization or implementation can resume.
- Preserve generic forensic provenance only; do not create either future S2
  authorization or implementation card, code, evidence or runtime state.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `changerail-release-ci`: add the publish-before-creation decision and
  bounded proof contract for future psutil-backed S2.

## Impact

This change touches only its board card, OpenSpec artifacts and the
`changerail-release-ci` specification. Delivery synchronizes and archives the
same change. Production code, dependency manifests, tests, bootstrap scripts,
admission logic, workflow, release baseline, CI, runtime state, successor
cards, review, commit and push remain unchanged.
