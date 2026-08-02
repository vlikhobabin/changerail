## Why

Series `020` needs a deterministic end-to-end guard for one-command delivery.
Existing focused smokes cover runner pieces, manifests, verdicts and evidence,
but they do not prove that an accepted `deliver-ready` card can pass through the
whole runner-supervised path and stop fail-closed on the new resume and review
budget contracts.

## What Changes

- Add a bounded local integration fixture that starts from a `2.todo`
  deliver-ready card and invokes one orchestration entrypoint.
- Exercise successful planning, delivery, independent review, scoped publish,
  board finalization and ignored manifest/status/evidence outputs against a
  temporary repository and local bare remote.
- Add deterministic failure-path coverage for transient preflight resume and
  stale verdict or exhausted review-budget `NO-GO` stops.
- Include the new smoke in the local release baseline and release inventory
  documentation.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-delivery-runner`: require one-command delivery regression smoke
  coverage for success, transient preflight resume and fail-closed review
  failure paths without live network or real consumer repositories.
- `changerail-release-discipline`: require the new one-command delivery smoke to
  be part of the local release baseline inventory.

## Impact

- Affected scripts: `scripts/smoke-delivery-runner.py`,
  `scripts/run-release-baseline.py`.
- Affected docs/specs: delivery runner and release discipline OpenSpec specs,
  release baseline documentation or inventory text as needed.
- Runtime artifacts stay under ignored `.runtime/changerail/`; the tracked
  payload must not include raw logs, local state, credentials or live network
  dependencies.
