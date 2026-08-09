## 1. Schemas And CLI

- [x] 1.1 Add `changerail.maintenance-quality-rollup.v1` JSON Schema and schema validation helper.
- [x] 1.2 Add `changerail.maintenance-proposal-decision.v1` JSON Schema and schema validation helper.
- [x] 1.3 Add `quality` parser options to `scripts/changerail_maintenance.py` for report, history, triage, proposal, text, JSON and CSV inputs.
- [x] 1.4 Implement quality rollup metric calculation with explicit `unknown` status for missing optional inputs.
- [x] 1.5 Implement stable text, JSON and `metric,value,unit,status` CSV output without changing `bin/changerail-delivery-metrics`.

## 2. Metric Semantics

- [x] 2.1 Calculate latest complete report open, accepted and waived counts.
- [x] 2.2 Calculate resolved findings only from ordered complete report snapshots and render incomplete history as `unknown`.
- [x] 2.3 Calculate catalog coverage, stale/generated and board dedup metrics from validated tracked state and exact maintenance origin markers.
- [x] 2.4 Calculate time-to-triage and accepted/rejected proposal counts only from schema-valid optional inputs.
- [x] 2.5 Keep instruction byte metrics `unknown` until a schema-valid producer exists.

## 3. Fixtures And Tests

- [x] 3.1 Add public-safe quality fixtures for complete/incomplete reports and resolved-count history.
- [x] 3.2 Add proposal-decision fixtures for accepted, rejected and invalid records.
- [x] 3.3 Extend `scripts/smoke-repository-knowledge.py` to cover text, JSON, CSV, unknown optional metrics and read-only behavior.
- [x] 3.4 Extend `scripts/smoke-contract-schemas.py` for the new schema files.

## 4. Verification

- [x] 4.1 Run `./bin/openspec validate add-maintenance-quality-rollup --strict`.
- [x] 4.2 Run `python3 scripts/smoke-repository-knowledge.py`.
- [x] 4.3 Run `python3 scripts/smoke-contract-schemas.py`.
- [x] 4.4 Run `git diff --check`.
- [x] 4.5 Run `python3 scripts/public-surface-scan.py`.
