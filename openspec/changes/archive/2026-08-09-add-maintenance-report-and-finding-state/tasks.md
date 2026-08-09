## 1. Schemas and contracts
- [x] Add `schemas/changerail-maintenance-report.schema.json`.
- [x] Add `schemas/changerail-maintenance-state.schema.json`.
- [x] Update `docs/changerail-contracts.md` with the new lifecycle contracts.

## 2. Lifecycle normalization
- [x] Implement scan-to-report normalization in
  `scripts/changerail_repository_knowledge.py`.
- [x] Implement identity and evidence fingerprint helpers with safe canonical
  JSON material.
- [x] Implement runtime state load/write with corrupt-version fail-closed
  behavior.
- [x] Add `bin/changerail-maintenance report --json [--write-state]`.

## 3. Verification fixtures
- [x] Add smoke coverage for valid and invalid lifecycle report schemas.
- [x] Add tests for identity stability, evidence-change semantics and
  path/secret fail-closed behavior.
- [x] Add tests for atomic state write, same-state continuity and corrupt-state
  rejection.
- [x] Add tests proving explicit state writes cannot target tracked paths
  outside `.runtime/changerail/maintenance/`.

## 4. Verification
- [x] Run `python3 scripts/smoke-contract-schemas.py`.
- [x] Run `python3 scripts/smoke-repository-knowledge.py`.
- [x] Run `openspec validate add-maintenance-report-and-finding-state --strict`.
- [x] Run `openspec validate --all --strict`.
- [x] Run `git diff --check`.
