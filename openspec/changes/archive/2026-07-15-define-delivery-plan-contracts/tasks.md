## 1. Contract Schemas

- [x] 1.1 Add `schemas/changerail-delivery-plan.schema.json` for the JSON plan contract.
- [x] 1.2 Add `schemas/changerail-delivery-plan-status.schema.json` for aggregate queue status.
- [x] 1.3 Add schema smoke fixtures and negative safety fixtures to `scripts/smoke-contract-schemas.py`.

## 2. Specs And Docs

- [x] 2.1 Update `docs/changerail-contracts.md` with plan and status contract semantics.
- [x] 2.2 Keep `changerail.delivery-run.v1` documentation backward compatible and reference child records from queue status.

## 3. Verification

- [x] 3.1 Run `python3 scripts/smoke-contract-schemas.py`.
- [x] 3.2 Run `./bin/openspec validate define-delivery-plan-contracts --strict`.
- [x] 3.3 Run `./bin/openspec validate --all --strict`.
- [x] 3.4 Run `git diff --check`, including new untracked schema and artifact files.
- [x] 3.5 Run `python3 scripts/public-surface-scan.py`.
