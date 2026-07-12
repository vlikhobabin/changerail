## 1. Contracts And Helpers

- [x] 1.1 Rename schema files from `schemas/opsx-*.schema.json` to `schemas/changerail-*.schema.json`.
- [x] 1.2 Update schema ids from `opsx.*.v1` to `changerail.*.v1` and adjust validators/smoke fixtures.
- [x] 1.3 Rename helper wrappers and modules from `opsx-*`/`opsx_*` to `changerail-*`/`changerail_*`.
- [x] 1.4 Update delivery runner prompts, metrics defaults, review history paths and runtime defaults from `.runtime/opsx` to `.runtime/changerail`.
- [x] 1.5 Update docs and skill references for renamed helpers and contract ids.

## 2. Verification

- [x] 2.1 Run JSON schema parsing checks for all `schemas/changerail-*.schema.json`.
- [x] 2.2 Run review verdict, delivery manifest, delivery runner and delivery metrics smoke tests.
- [x] 2.3 Run `./bin/openspec validate rename-contracts-helpers-runtime --strict`.
- [x] 2.4 Run `git diff --check`.
- [x] 2.5 Scan active tracked files for stale canonical `opsx.*.v1`, `opsx-*.schema.json`, `bin/opsx-*`, `scripts/opsx_*` and `.runtime/opsx` defaults.
