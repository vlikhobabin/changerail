# Improve delivery-plan runner operator UX

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Consumer adoption feedback from a ChangeRail delivery-plan setup on
  2026-07-24.
- Follow-up split from
  `openspec/board/1.backlog/harden-consumer-codex-auth-setup.md`.
- `docs/how-it-works.md`
- `docs/changerail-contracts.md`
- `docs/consumer-adoption-runbook.md`
- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-plan.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`

## Summary
Delivery-plan orchestration works, but the operator experience for first-time
queue setup is still too manual and noisy.

Three issues should be handled as one UX-oriented story:

- `preflight-plan` aggregate output can hide the actionable child failure by
  embedding a truncated JSON snippet. Operators should see a compact line such
  as `example-card: CODEX auth fail` or `example-card: workspace dirty state
  fail`, while full child status remains available as runtime evidence.
- Documentation should be explicit that a consumer repository does not
  necessarily need its own tracked `bin/codex`; the runner can launch through
  the ChangeRail single-card runner and set `CODEX_WORKDIR`/`CODEX_HOME` for
  the effective workspace.
- Operators need a helper or documented example for producing
  `changerail.delivery-plan.v1` JSON from a small ordered list of board cards,
  so typical serial delivery of 3-5 cards does not require hand-writing the
  whole plan.

The change should stay generic and public-safe: examples use
`/opt/example-project`, `/opt/example-workspace` and `example-card`, not real
consumer names or local paths.

## Acceptance
- `preflight-plan` reports child preflight failures in aggregate output with a
  concise card id, failed check name and short reason, without relying on a
  truncated JSON blob.
- Aggregate status still references full child `changerail.delivery-run.v1`
  status records and does not inline raw stdout/stderr logs.
- `status-plan --json` preserves schema compatibility or updates the schema and
  specs intentionally if new structured fields are added.
- Docs explain launcher semantics for queue plans: plan runner launches the
  ChangeRail single-card runner, the child runner launches Codex, and
  `CODEX_WORKDIR`/effective `CODEX_HOME` select the consumer workspace.
- Docs avoid implying that every consumer must have a tracked repo-local
  `bin/codex`; when a repo-local launcher is optional or absent, the supported
  invocation path is clear.
- A helper command, dry-run mode or documented recipe can generate a valid
  `changerail.delivery-plan.v1` file from an ordered list of card paths and
  optional dependencies.
- The generated example plan validates through `plan` and `preflight-plan`
  without live child delivery.
- Smoke coverage includes compact child-failure reporting, launcher docs or
  command resolution expectations, and plan-generation validation.
- Public-surface scans pass without private consumer names, local absolute
  paths, credentials, auth files, runtime logs or machine-specific status in
  tracked payload.

## Change Set
- `compact-plan-preflight-child-diagnostics`
- `document-queue-launcher-semantics`
- `generate-delivery-plan-from-card-list`
- `delivery-plan-ux-smoke-and-docs`

## Verify
- `python3 -m py_compile bin/changerail-delivery-runner` - pass.
- `python3 scripts/smoke-delivery-runner.py` - pass.
- `python3 scripts/smoke-contract-schemas.py` - pass with 7 schemas.
- `python3 -m json.tool .mcp.json` - pass.
- `.codex/config.toml` parse via `tomllib` - pass.
- `./bin/openspec validate compact-plan-preflight-child-diagnostics --strict` - pass
- `./bin/openspec validate document-queue-launcher-semantics --strict` - pass
- `./bin/openspec validate generate-delivery-plan-from-card-list --strict` - pass
- `./bin/openspec validate delivery-plan-ux-smoke-and-docs --strict` - pass
- `./bin/openspec validate changerail-delivery-runner --strict` - pass.
- `./bin/openspec validate changerail-contracts --strict` - pass.
- `./bin/openspec validate --all --strict` - pass before archive with 17/17
  items and after archive with 13/13 items.
- `python3 scripts/public-surface-scan.py` - pass with 544 files scanned and
  0 findings.
- `python3 scripts/run-release-baseline.py` - pass with 25/25 steps.
- `git diff --check` - pass before archive and after archive.

## Archive
- `openspec/changes/archive/2026-07-26-compact-plan-preflight-child-diagnostics/`
- `openspec/changes/archive/2026-07-26-document-queue-launcher-semantics/`
- `openspec/changes/archive/2026-07-26-generate-delivery-plan-from-card-list/`
- `openspec/changes/archive/2026-07-26-delivery-plan-ux-smoke-and-docs/`

## Related
- `openspec/board/1.backlog/harden-consumer-codex-auth-setup.md`
- `bin/changerail-delivery-runner`
- `docs/how-it-works.md`
- `docs/changerail-contracts.md`
- `docs/consumer-adoption-runbook.md`
- `docs/board-and-two-agent-feature-flow.md`
- `schemas/changerail-delivery-plan.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `openspec/specs/changerail-contracts/spec.md`
- `scripts/smoke-delivery-runner.py`
- `scripts/smoke-contract-schemas.py`
- `scripts/public-surface-scan.py`

## Result
implemented, verified, synced, archived, reviewed and published

Published reviewed payload as `11d004e`; push status `pushed` on `main`/`origin`.

## Next
- done

## Change Plan Notes
Ordered changes are apply-ready.

## Change 1: `compact-plan-preflight-child-diagnostics`

### Why
When a child preflight fails, the aggregate status should make the actionable
reason obvious without requiring the operator to inspect nested runtime files
first.

### Goal
Capture and display concise child failure summaries in `preflight-plan` and
`status-plan`, while preserving full child status references as runtime
evidence.

### Acceptance
- A missing-auth or dirty-workspace child preflight produces a short aggregate
  reason such as `example-card: CODEX auth fail`.
- Full child status path remains available for deeper inspection.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-26-compact-plan-preflight-child-diagnostics/`

## Change 2: `document-queue-launcher-semantics`

### Why
Operators can misread the queue runner as requiring a tracked `bin/codex` in
every consumer repository.

### Goal
Clarify which launcher runs at each layer and how `CODEX_WORKDIR` and
effective `CODEX_HOME` bind delivery to the consumer workspace.

### Acceptance
- Docs distinguish plan runner, single-card runner and Codex launcher.
- Examples remain generic and do not introduce private paths.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-26-document-queue-launcher-semantics/`

## Change 3: `generate-delivery-plan-from-card-list`

### Why
Typical serial delivery of several cards should not require hand-writing the
full JSON plan.

### Goal
Add a helper command or documented recipe that takes an ordered list of card
paths, workspace alias/path and optional dependencies, then emits a valid
`changerail.delivery-plan.v1` file.

### Acceptance
- Generated plan validates with `plan --json`.
- The helper supports a simple serial plan and a small dependency graph.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-26-generate-delivery-plan-from-card-list/`

## Change 4: `delivery-plan-ux-smoke-and-docs`

### Why
The improvements span CLI output, schemas and docs, so focused regression
coverage is needed.

### Goal
Extend smoke tests and docs/examples for compact diagnostics, launcher
semantics and generated plan validation.

### Acceptance
- `scripts/smoke-delivery-runner.py` or equivalent focused smoke covers the new
  behavior.
- Public-surface and release baseline checks remain green.

### Depends On
- `compact-plan-preflight-child-diagnostics`
- `document-queue-launcher-semantics`
- `generate-delivery-plan-from-card-list`

### Related
- `openspec/changes/archive/2026-07-26-delivery-plan-ux-smoke-and-docs/`

## Log
- 2026-07-24T04:46:19Z card created from delivery-plan operator UX feedback.
- 2026-07-26T00:00:00Z fast-forward planning created four apply-ready
  OpenSpec changes and moved the card to `3.inprogress`.
- 2026-07-26T10:00:42Z implemented runner, docs and smoke coverage; synced
  specs and archived all four OpenSpec changes.
- 2026-07-26T10:14:00Z publish finalized card into `4.done`, pushed reviewed
  payload commit `11d004e` to `origin/main`, and retained ignored runtime
  manifest/review evidence outside tracked payload.
