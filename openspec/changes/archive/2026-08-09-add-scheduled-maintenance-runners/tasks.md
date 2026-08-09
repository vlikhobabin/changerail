## 1. Runner status contract

- [x] 1.1 Add `schemas/changerail-maintenance-run.schema.json`.
- [x] 1.2 Add positive and negative schema fixtures for
  `changerail.maintenance-run.v1`.
- [x] 1.3 Extend `scripts/smoke-contract-schemas.py` to validate the new
  schema and fixtures.
- [x] 1.4 Update `docs/changerail-contracts.md` with maintenance run status
  fields and runtime path.

## 2. Maintenance runner

- [x] 2.1 Add `bin/changerail-maintenance-runner` through the shared Python
  runtime selector.
- [x] 2.2 Add native Windows wrapper `bin/changerail-maintenance-runner.cmd`.
- [x] 2.3 Implement scan mode with read-only deterministic scan/report
  execution and no Codex auth requirement.
- [x] 2.4 Implement ignored run status writes under
  `.runtime/changerail/maintenance/runs/<run-id>/`.
- [x] 2.5 Implement atomic non-overlap lock handling, bounded timeout and
  stale-lock diagnostics.
- [x] 2.6 Implement optional triage mode validation for schema-valid
  annotations/previews without scraping human prose.

## 3. Scheduler examples and smoke coverage

- [x] 3.1 Add public-safe GitHub Actions maintenance example with
  `contents: read` and artifact upload.
- [x] 3.2 Add systemd and Codex scheduled task examples with repository cwd,
  bounded timeout and non-overlap guidance.
- [x] 3.3 Add CI separation example that keeps read-only analysis distinct from
  write/API jobs.
- [x] 3.4 Add focused smoke coverage for scan-only no-auth mode, timeout, lock,
  status schema and invalid triage child output.

## 4. Verification

- [x] 4.1 Run `python3 -m py_compile` for changed Python runner/test files.
- [x] 4.2 Run `python3 scripts/smoke-contract-schemas.py`.
- [x] 4.3 Run focused maintenance runner smoke tests.
- [x] 4.4 Run `python3 scripts/public-surface-scan.py`.
- [x] 4.5 Run `./bin/openspec validate add-scheduled-maintenance-runners
  --strict`.
- [x] 4.6 Run `./bin/openspec validate --all --strict`.
- [x] 4.7 Run `git diff --check`.
