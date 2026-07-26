## 1. Runner Diagnostics

- [x] 1.1 Replace child preflight JSON snippets in aggregate output with compact
      child failure summaries.
- [x] 1.2 Preserve full child status references through existing
      `run_status_path` fields.
- [x] 1.3 Ensure `status-plan --json` remains valid against the current plan
      status schema.

## 2. Smoke Coverage

- [x] 2.1 Add smoke coverage for compact child preflight failure reporting.
- [x] 2.2 Add validation that aggregate status does not inline raw child
      stdout/stderr logs.

## 3. Verification

- [x] 3.1 Run `python3 -m py_compile bin/changerail-delivery-runner`.
- [x] 3.2 Run `python3 scripts/smoke-delivery-runner.py`.
- [x] 3.3 Run `./bin/openspec validate compact-plan-preflight-child-diagnostics --strict`.
- [x] 3.4 Run `./bin/openspec validate --all --strict`.
- [x] 3.5 Run `git diff --check`.
