## 1. Drift Gate Implementation

- [x] 1.1 Add executable `scripts/smoke-drift.py` with config/CLI inventory,
  shallow workspace-root scanning and default ignored runtime report output.
- [x] 1.2 Implement project classification using `bin/verify-project --json`,
  configured legacy roots, OPSX-like indicators and explicit excludes.
- [x] 1.3 Emit `opsx.drift-gate.v1` JSON with aggregate summary and per-project
  classification evidence.

## 2. Verification Fixtures

- [x] 2.1 Create ignored runtime fixtures that cover `opsx_source`,
  `legacy_source`, `broken_wiring`, `disconnected` and `explicitly_excluded`.
- [x] 2.2 Run `python3 scripts/smoke-drift.py --config <runtime-config>` and
  confirm the expected red result when drift classes are present.
- [x] 2.3 Run `python3 scripts/smoke-drift.py --project <valid-fixture>` and
  confirm the expected green result for only OPSX source projects.

## 3. Docs, Specs And Safety

- [x] 3.1 Update public docs or README references for the implemented drift
  gate without adding real local inventory.
- [x] 3.2 Run `python3 -m py_compile scripts/smoke-drift.py`.
- [x] 3.3 Run `openspec validate add-workspace-drift-gate --strict`.
- [x] 3.4 Run `openspec validate --all --strict`.
- [x] 3.5 Run `git diff --check` plus a text whitespace scan over modified and
  untracked files.
- [x] 3.6 Run a targeted public-surface scan for private paths, machine-local
  inventory, secrets and runtime report leakage.
