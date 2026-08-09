## Why

Recurring maintenance scans need a scheduler-neutral runner with bounded
execution and structured status. Embedding scheduler behavior into the core CLI
or relying on human prose would make unattended audit brittle and harder to
verify.

## What Changes

- Добавить `bin/changerail-maintenance-runner` и native Windows wrapper
  `bin/changerail-maintenance-runner.cmd`.
- Определить runner modes `scan` и optional agent `triage`.
- Опубликовать structured status contract `changerail.maintenance-run.v1` под
  ignored `.runtime/changerail/maintenance/runs/<run-id>/`.
- Реализовать read-only scan mode, который работает без Codex authentication.
- Добавить lock, timeout, budget и child-output validation для non-overlapping
  bounded runs.
- Добавить public least-privilege scheduler examples for GitHub Actions,
  systemd, Codex scheduled tasks and CI separation.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-repository-knowledge`: добавить scheduler-neutral maintenance
  runner behavior, runtime status semantics and scheduler example boundaries.
- `changerail-contracts`: добавить public `changerail.maintenance-run.v1`
  schema и fixture-backed validation.

## Impact

- `bin/`, `scripts/`, `schemas/`, `fixtures/` and smoke tests receive the runner
  and status contract.
- `examples/maintenance/` gets public-safe scheduler examples.
- `docs/changerail-contracts.md` documents the new run status.
- Existing deterministic `bin/changerail-maintenance scan/report` behavior
  remains the source of truth for scan output.
