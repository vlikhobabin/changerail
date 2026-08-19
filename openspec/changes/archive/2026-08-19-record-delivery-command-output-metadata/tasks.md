## 1. Runner metadata collection

- [x] 1.1 Parse structured child command events for stdout/stderr byte counts
  and truncation indicators when present.
- [x] 1.2 Add per-command classification for process failure, runner
  truncation, successful bounded result and unknown output state.
- [x] 1.3 Add documented default threshold handling with operator override if
  appropriate.
- [x] 1.4 Keep raw command payloads out of `status.json`.

## 2. Contract schema

- [x] 2.1 Extend `schemas/changerail-delivery-run.schema.json` with optional
  command output metadata fields.
- [x] 2.2 Add schema smoke fixtures for valid metadata, legacy records and raw
  payload rejection.
- [x] 2.3 Ensure status compactness remains bounded by top-N/aggregate
  behavior.

## 3. Verification

- [x] 3.1 Run `python3 -m py_compile bin/changerail-delivery-runner scripts/changerail_contract_schema.py`.
- [x] 3.2 Run `python3 scripts/smoke-contract-schemas.py`.
- [x] 3.3 Run `python3 scripts/smoke-delivery-runner.py`.
- [x] 3.4 Run `./bin/openspec validate "record-delivery-command-output-metadata" --strict`.
- [x] 3.5 Run `./bin/openspec validate --all --strict`.
- [x] 3.6 Run `git diff --check`.
