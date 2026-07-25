## 1. Runner Diagnostics

- [x] 1.1 Update `bin/changerail-delivery-runner` missing-auth diagnostic text.
- [x] 1.2 Update stale `CODEX_HOME` symlink diagnostic text.
- [x] 1.3 Keep check names and status schema unchanged.

## 2. Smoke

- [x] 2.1 Extend `scripts/smoke-delivery-runner.py` to assert missing-auth
  remediation text.
- [x] 2.2 Extend stale-symlink smoke assertions for remediation text.
- [x] 2.3 Confirm smoke output does not contain credential contents or
  token-like values.

## 3. Verification

- [x] 3.1 Run `python3 scripts/smoke-delivery-runner.py`.
- [x] 3.2 Run `./bin/openspec validate "runner-auth-remediation-diagnostics" --strict`.
- [x] 3.3 Run `./bin/openspec validate --all --strict`.
- [x] 3.4 Run `git diff --check`.

## Verification Notes

- `python3 scripts/smoke-delivery-runner.py` passed.
- `./bin/openspec validate "runner-auth-remediation-diagnostics" --strict` passed.
- `./bin/openspec validate --all --strict` passed with 15 items.
- `git diff --check` passed.
- `python3 -m py_compile bin/changerail-delivery-runner scripts/smoke-delivery-runner.py` passed.
