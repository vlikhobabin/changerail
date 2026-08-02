## 1. Matrix Runner

- [x] 1.1 Add `scripts/smoke-windows-matrix.py` with default local mode,
  `--json`, retained report output and schema
  `changerail.windows-smoke-matrix.v1`.
- [x] 1.2 Compose mandatory local checks for entrypoints, generated-copy
  wiring, verifier/drift fixtures and Windows wiring Git safety.
- [x] 1.3 Add sanitized diagnostics and runtime report retention under ignored
  `.runtime/changerail/windows-smoke/`.

## 2. Live Host And Repeatability

- [x] 2.1 Add explicit live mode using ignored
  `internal/windows-lab-inventory.json`, generic host ids and existing Windows
  lab probe conventions.
- [x] 2.2 Add repeat-after-cleanup mode and status-mismatch reporting.
- [x] 2.3 Ensure missing or failed live host coverage records an explicit
  blocker/caveat instead of claiming two-host coverage.

## 3. Release Baseline Integration

- [x] 3.1 Add the platform-neutral matrix command to
  `scripts/run-release-baseline.py`.
- [x] 3.2 Add the matrix command to tracked CI workflow and
  `scripts/smoke-release-ci.py` required command inventory.

## 4. Verification

- [x] 4.1 Run `bin/openspec status --change add-windows-smoke-matrix-runner --json`.
- [x] 4.2 Run `bin/openspec instructions apply --change add-windows-smoke-matrix-runner --json`.
- [x] 4.3 Run `bin/openspec validate add-windows-smoke-matrix-runner --strict`.
- [x] 4.4 Run `python3 -m py_compile scripts/smoke-windows-matrix.py`.
- [x] 4.5 Run `python3 scripts/smoke-windows-matrix.py --json`.
- [x] 4.6 Run `python3 scripts/smoke-release-ci.py`.
- [x] 4.7 Run `python3 scripts/public-surface-scan.py`.
- [x] 4.8 Run `git diff --check` and an explicit whitespace scan for new
  untracked OpenSpec artifacts.
