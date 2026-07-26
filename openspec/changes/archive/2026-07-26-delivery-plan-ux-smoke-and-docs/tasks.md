## 1. Smoke Coverage

- [x] 1.1 Extend `scripts/smoke-delivery-runner.py` for compact child failure
      reporting.
- [x] 1.2 Extend smoke coverage for `generate-plan`, `plan` and
      `preflight-plan`.
- [x] 1.3 Add docs expectation checks for queue launcher semantics and optional
      consumer repo-local `bin/codex` wording.

## 2. Verification

- [x] 2.1 Run `python3 scripts/smoke-delivery-runner.py`.
- [x] 2.2 Run `python3 scripts/public-surface-scan.py`.
- [x] 2.3 Run `python3 scripts/run-release-baseline.py`.
- [x] 2.4 Run `./bin/openspec validate delivery-plan-ux-smoke-and-docs --strict`.
- [x] 2.5 Run `./bin/openspec validate --all --strict`.
- [x] 2.6 Run `git diff --check`.
