## Why

Supervisor-side publish-target preflight does not prove that the later delivery
child can resolve the same Git/SSH target under its effective launcher,
`CODEX_HOME`, `CODEX_WORKDIR`, permission profile and Git/SSH environment.
The published investigation selected a child-equivalent receipt so predictable
child failures stop an aggregate run before locks and child delivery launch.

## What Changes

- Add child-equivalent publish-target preflight to delivery-plan admission.
- Re-run child-equivalent publish-target preflight before dispatching each
  later unresolved card during `run-plan` and `resume-plan`.
- Preserve sanitized child failure class, retryability, attempt count and
  `run_status_path` in existing single-card and aggregate status fields.
- Classify child publish-target failure as aggregate `BLOCKED` with
  `terminal_reason: publish_target_preflight_failed`, not `unpublished_card`.
- Keep explicit `--no-push` local-only semantics unchanged.
- Do not add required runner/status wire fields.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-delivery-runner`: delivery-plan admission, dispatch-time
  revalidation and structured terminal status for child-equivalent
  publish-target preflight.

## Impact

- `bin/changerail-delivery-runner`
- `scripts/smoke-delivery-runner.py`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `docs/changerail-contracts.md`
- Existing schemas `changerail.delivery-run.v1` and
  `changerail.delivery-plan-status.v1` are reused without new required fields.
