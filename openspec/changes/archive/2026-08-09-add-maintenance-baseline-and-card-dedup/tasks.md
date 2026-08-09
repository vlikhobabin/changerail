## 1. Baseline and annotation schemas
- [x] Add `schemas/changerail-maintenance-baseline.schema.json`.
- [x] Add `schemas/changerail-maintenance-triage.schema.json`.
- [x] Add optional tracked `.changerail/maintenance-baseline.yaml` fixture.
- [x] Update `docs/changerail-contracts.md` with baseline, waiver and triage
  contracts.

## 2. Baseline and triage commands
- [x] Implement baseline load/validation and suppression evaluation helpers.
- [x] Implement `bin/changerail-maintenance accept-baseline --json [--write]`.
- [x] Implement `bin/changerail-maintenance triage --annotations <path> --json`.
- [x] Ensure preview mode writes only ignored runtime preview artifacts or
  stdout.

## 3. Board-card bridge
- [x] Implement `bin/changerail-maintenance cards --json [--write]`.
- [x] Scan all board lanes for exact `Maintenance Origin:
  <sha256 fingerprint>` markers before writing.
- [x] Update existing cards by identity and create new backlog cards only when
  no marker exists.
- [x] Sanitize card title, summary and evidence references.

## 4. Verification
- [x] Add schema fixtures for valid/invalid baseline, waivers and triage
  annotations.
- [x] Add smoke coverage for preview/default no-mutation and explicit-write
  scope.
- [x] Add smoke coverage for board dedup across all lanes and evidence summary
  update.
- [x] Add smoke coverage for active date-only waivers and unsafe report-sourced
  card material rejection.
- [x] Run `python3 scripts/smoke-contract-schemas.py`.
- [x] Run `python3 scripts/smoke-repository-knowledge.py`.
- [x] Run `openspec validate add-maintenance-baseline-and-card-dedup --strict`.
- [x] Run `openspec validate --all --strict`.
- [x] Run `git diff --check`.
