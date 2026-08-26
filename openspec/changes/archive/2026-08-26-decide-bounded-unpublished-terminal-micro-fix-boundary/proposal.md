## Why

The published psutil S2 decision and authorization do not permit resuming or
publishing an unpublished candidate that exhausted its cycle budget. A new
decision is needed to allow one narrowly bounded v3 micro-fix without carrying
terminal material forward as authority or evidence.

## What Changes

- Add one docs-only release-CI decision that blocks an exact future v3
  authorization and successor, with their reciprocal six-field and two-field
  authorization objects.
- Define the admission boundary for the only permitted micro-fix: clean start
  from its own authorization HEAD, unchanged authorized production paths and
  scope, `<=499` added production LOC, and independent R1-R7 proof.
- Define R7 precisely: pipe EOF is stream state, not completion; completion
  requires observed leader termination or execution timeout, followed by
  cleanup.
- Keep v3 and downstream refresh structurally dormant until v3 publication;
  do not create either future card or reuse terminal forensic material.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `changerail-release-ci`: add the bounded unpublished-terminal micro-fix
  decision and its future v3 authorization, proof and dormancy contract.

## Impact

Only the decision card, same-slug OpenSpec artifacts, synchronized
`changerail-release-ci` specification and archive metadata change. Production
code, tests, runtime behavior, dependency manifests, CI, release baseline,
authorization/successor cards, review, commit and push remain unchanged.
