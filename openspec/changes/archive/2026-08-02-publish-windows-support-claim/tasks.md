## 1. Evidence Review

- [x] 1.1 Read the retained clean-clone lifecycle report and aggregate Windows
  matrix report.
- [x] 1.2 Classify per-host outcome, support caveats and evidence paths for
  public-safe tracked docs.

## 2. Documentation Updates

- [x] 2.1 Update `docs/compatibility.md` with final native Windows support
  claim, matrix, evidence paths and caveats.
- [x] 2.2 Update `docs/migration-guide.md` with native Windows `.cmd`,
  generated-copy, verification and refresh guidance.
- [x] 2.3 Update `docs/consumer-adoption-runbook.md` and release guidance with
  Windows support verification and blocker handling.

## 3. Verification

- [x] 3.1 Run `python3 scripts/smoke-windows-matrix.py --json`.
- [x] 3.2 Run `python3 scripts/run-release-baseline.py`.
- [x] 3.3 Run `python3 scripts/public-surface-scan.py`.
- [x] 3.4 Run `python3 scripts/public-surface-scan.py --history`.
- [x] 3.5 Run `openspec validate publish-windows-support-claim --strict`,
  `openspec validate --all --strict` and `git diff --check`.
