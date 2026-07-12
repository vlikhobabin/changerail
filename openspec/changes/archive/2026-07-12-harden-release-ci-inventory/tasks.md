## 1. CI inventory and lint gates
- [x] Add pinned release-gate Python tooling for `jsonschema` and `ruff`.
- [x] Add or update a tracked syntax inventory command that compiles all tracked
  Python helpers under `bin/` and `scripts/`.
- [x] Add `ruff check bin scripts` to CI and fix current lint failures without
  unrelated style churn.

## 2. Smoke and schema coverage
- [x] Add release schema validation smoke for all five public
  `changerail-*.schema.json` contracts.
- [x] Update CI to run delivery runner, delivery metrics, review fingerprint,
  review verdict validation, manifest, manifest derivation, archive diagnostics,
  bootstrap, verify, wiring, release workflow and generated drift fixture smoke.
- [x] Strengthen `scripts/smoke-release-ci.py` so it checks required command
  inventory, including the schema, lint, runner, metrics and fingerprint gates.

## 3. Verification
- [x] Run `python3 scripts/smoke-release-ci.py` and record the outcome.
  Outcome: pass, `summary: pass (39/39 passed, 0 failed)`.
- [x] Run `python3 scripts/smoke-contract-schemas.py` and record the outcome.
  Outcome: pass, `SMOKE_CONTRACT_SCHEMAS_OK (5 schemas)`.
- [x] Run `ruff check bin scripts` and record the outcome.
  Outcome: pass via `.runtime/changerail/ci-venv/bin/ruff check bin scripts`.
- [x] Run `openspec validate harden-release-ci-inventory --strict`.
  Outcome: pass.
