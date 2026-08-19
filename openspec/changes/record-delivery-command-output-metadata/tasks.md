## 1. Runner metadata collection

- [ ] 1.1 Parse structured child command events for stdout/stderr byte counts
  and truncation indicators when present.
- [ ] 1.2 Add per-command classification for process failure, runner
  truncation, successful bounded result and unknown output state.
- [ ] 1.3 Add documented default threshold handling with operator override if
  appropriate.
- [ ] 1.4 Keep raw command payloads out of `status.json`.

## 2. Contract schema

- [ ] 2.1 Extend `schemas/changerail-delivery-run.schema.json` with optional
  command output metadata fields.
- [ ] 2.2 Add schema smoke fixtures for valid metadata, legacy records and raw
  payload rejection.
- [ ] 2.3 Ensure status compactness remains bounded by top-N/aggregate
  behavior.

## 3. Verification

- [ ] 3.1 Run `python3 -m py_compile bin/changerail-delivery-runner scripts/changerail_contract_schema.py`.
- [ ] 3.2 Run `python3 scripts/smoke-contract-schemas.py`.
- [ ] 3.3 Run `python3 scripts/smoke-delivery-runner.py`.
- [ ] 3.4 Run `./bin/openspec validate "record-delivery-command-output-metadata" --strict`.
- [ ] 3.5 Run `./bin/openspec validate --all --strict`.
- [ ] 3.6 Run `git diff --check`.
