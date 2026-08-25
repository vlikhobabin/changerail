## Why

Published clean-lineage decision fixes the exact H successor, but deterministic
preflight may consume its bounded exception only from a separate clean tracked
`4.done` authorization source. This source must exist before the future H card
or implementation is created.

## What Changes

- Add one authorization board card with exactly one six-field investigation
  authorization object binding the published decision to the sole future H
  successor.
- State the independent H implementation boundary: `<=349` production LOC
  against its future published authorization HEAD, with no new authority or
  wire protocol.
- Add the corresponding `changerail-release-ci` relationship requirement and
  preserve reciprocal decision/authorization/future-successor lineage.
- Keep the payload docs-only: no successor card/code, production, test or
  runtime additions.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-release-ci`: publish the exact clean structural-history v3
  authorization source and its future successor reference policy.

## Impact

This affects only the authorization board card, its OpenSpec artifacts and the
release-CI specification. It changes no production code, tests, schemas,
parsers, helpers, workflows, CLI surface or runtime state; no history scan,
full baseline or live run is performed.
