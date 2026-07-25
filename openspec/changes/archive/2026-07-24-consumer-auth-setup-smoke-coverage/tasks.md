## 1. Smoke Coverage

- [x] 1.1 Ensure `scripts/smoke-bootstrap-project.py` covers default no-link,
  explicit auth link and missing-source failure.
- [x] 1.2 Ensure `scripts/smoke-verify-project.py` covers missing-auth,
  auth-marker and auth-env advisories.
- [x] 1.3 Ensure `scripts/smoke-delivery-runner.py` covers missing-auth,
  explicit `CODEX_HOME` and stale symlink remediation diagnostics.
- [x] 1.4 Ensure fake credential sentinel values are not printed or embedded in
  structured status assertions.

## 2. Verification

- [x] 2.1 Run `python3 scripts/smoke-bootstrap-project.py`.
- [x] 2.2 Run `python3 scripts/smoke-verify-project.py`.
- [x] 2.3 Run `python3 scripts/smoke-delivery-runner.py`.
- [x] 2.4 Run `python3 scripts/run-release-baseline.py`.
- [x] 2.5 Run `python3 scripts/public-surface-scan.py`.
- [x] 2.6 Run `git diff --check`.

## Verification Notes

- `python3 scripts/smoke-bootstrap-project.py` passed with 8/8 checks.
- `python3 scripts/smoke-verify-project.py` passed with 11/11 checks.
- `python3 scripts/smoke-delivery-runner.py` passed.
- `./bin/openspec validate "consumer-auth-setup-smoke-coverage" --strict` passed.
- `./bin/openspec validate --all --strict` passed with 14 items.
- `python3 scripts/public-surface-scan.py` passed with 517 files scanned and 0 findings.
- `git diff --check` passed.
- `python3 scripts/run-release-baseline.py` passed with 25/25 steps on rerun after one transient
  `smoke-openspec-archive-diagnostics.py` timeout.
