## 1. Verifier Inventory

- [x] 1.1 Add `changerail-maintenance-quality-rollup.schema.json` to the opted-in maintenance schema inventory.
- [x] 1.2 Add `changerail-maintenance-proposal-decision.schema.json` to the opted-in maintenance schema inventory.
- [x] 1.3 Update bootstrap/verify smoke expectations for complete maintenance schema coverage.
- [x] 1.4 Preserve maintenance opt-out behavior for consumers with no maintenance artifacts.

## 2. Fail-Closed Fixtures

- [x] 2.1 Add or update POSIX fixture coverage for missing quality/proposal maintenance schemas.
- [x] 2.2 Add or update generated-copy fixture coverage for stale or project-owned maintenance contract artifacts where applicable.
- [x] 2.3 Confirm `verify-project` still does not run full maintenance scan as part of the generic verification path.

## 3. Verification

- [x] 3.1 Run `python3 -m py_compile bin/verify-project scripts/smoke-verify-project.py scripts/smoke-bootstrap-project.py`.
- [x] 3.2 Run `python3 scripts/smoke-verify-project.py`.
- [x] 3.3 Run `python3 scripts/smoke-bootstrap-project.py`.
- [x] 3.4 Run `./bin/openspec validate complete-maintenance-consumer-verification --strict`.
- [x] 3.5 Run `git diff --check`.
