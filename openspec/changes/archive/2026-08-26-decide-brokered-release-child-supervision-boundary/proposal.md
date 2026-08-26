## Why

The terminal v3 attempt proved that caller-global child discovery is an
ambiguous ownership model: an unrelated pre-existing caller child can create a
later descendant that is indistinguishable from a reparented target process.
A separate architecture decision is required before any further supervisor
implementation can be authorized.

## What Changes

- Add one docs-only release-CI decision for a dedicated broker subprocess that
  becomes subreaper before it launches the target and owns only its own process
  tree.
- Define a bounded, versioned parent-broker protocol and fail-closed completion,
  timeout and cleanup semantics.
- Define the exact future v4 authorization and implementation lineage, a
  `<=499` production LOC boundary and one bounded repair/re-review allowance.
- Keep v4 and downstream activation dormant; do not create successor code or
  reuse terminal v3 evidence.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `changerail-release-ci`: add the broker-owned process-tree decision,
  protocol, proof, lineage and dormancy boundary.

## Impact

Only the decision card, same-slug OpenSpec artifacts, synchronized
`changerail-release-ci` specification and archive metadata change. Production
code, tests, dependencies, runtime behavior, CI, release baseline, future
cards, review, commit and push remain unchanged.
