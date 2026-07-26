## 1. Runner Helper

- [x] 1.1 Add `generate-plan` argument parsing and plan construction.
- [x] 1.2 Validate generated payload through the existing plan schema helper.
- [x] 1.3 Support ordered serial plans and optional dependency declarations.

## 2. Documentation

- [x] 2.1 Document the helper command and a public-safe example.
- [x] 2.2 State that generated JSON is still the canonical
      `changerail.delivery-plan.v1` contract.

## 3. Verification

- [x] 3.1 Add smoke coverage proving generated plans validate through `plan`.
- [x] 3.2 Add smoke coverage proving generated plans pass `preflight-plan`
      without live child delivery.
- [x] 3.3 Run `python3 -m py_compile bin/changerail-delivery-runner`.
- [x] 3.4 Run `python3 scripts/smoke-delivery-runner.py`.
- [x] 3.5 Run `./bin/openspec validate generate-delivery-plan-from-card-list --strict`.
- [x] 3.6 Run `./bin/openspec validate --all --strict`.
- [x] 3.7 Run `git diff --check`.
