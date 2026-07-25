## 1. Verification Advisory

- [x] 1.1 Add non-fatal advisory modeling to `bin/verify-project`.
- [x] 1.2 Detect `.codex/auth.json`, `.codex/auth.toml` and supported auth
  environment variables without reading credential contents.
- [x] 1.3 Emit advisory details in text and JSON output without changing
  mandatory check exit semantics.

## 2. Smoke

- [x] 2.1 Extend `scripts/smoke-verify-project.py` for missing auth advisory.
- [x] 2.2 Extend smoke coverage for project-local auth marker and auth
  environment variable readiness.

## 3. Verification

- [x] 3.1 Run `python3 scripts/smoke-verify-project.py`.
- [x] 3.2 Run `./bin/openspec validate "verify-project-delivery-readiness-advisory" --strict`.
- [x] 3.3 Run `./bin/openspec validate --all --strict`.
- [x] 3.4 Run `git diff --check`.

## Verification Notes

- `python3 scripts/smoke-verify-project.py` passed with 11/11 checks.
- `./bin/openspec validate "verify-project-delivery-readiness-advisory" --strict` passed.
- `./bin/openspec validate --all --strict` passed with 16 items.
- `git diff --check` passed.
- `python3 -m py_compile bin/verify-project scripts/smoke-verify-project.py` passed.
