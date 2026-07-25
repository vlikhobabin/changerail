## 1. Bootstrap CLI

- [x] 1.1 Add `--link-codex-auth <auth-json-path>` parsing to
  `bin/bootstrap-project`.
- [x] 1.2 Create `<target>/.codex/auth.json` as an opt-in symlink without
  reading or printing credential contents.
- [x] 1.3 Make missing or non-file auth source fail before bootstrap reports
  success.
- [x] 1.4 Include the auth link in dry-run planning.

## 2. Documentation And Smoke

- [x] 2.1 Document the opt-in bootstrap command in
  `docs/consumer-adoption-runbook.md`.
- [x] 2.2 Extend `scripts/smoke-bootstrap-project.py` for default no-link,
  successful auth link and missing-source failure.

## 3. Verification

- [x] 3.1 Run `python3 scripts/smoke-bootstrap-project.py`.
- [x] 3.2 Run `./bin/openspec validate "bootstrap-opt-in-auth-link" --strict`.
- [x] 3.3 Run `./bin/openspec validate --all --strict`.
- [x] 3.4 Run `git diff --check`.

## Verification Notes

- `python3 scripts/smoke-bootstrap-project.py` passed with 8/8 checks.
- `./bin/openspec validate "bootstrap-opt-in-auth-link" --strict` passed.
- `./bin/openspec validate --all --strict` passed with 17 items.
- `git diff --check` passed.
- `python3 -m py_compile bin/bootstrap-project scripts/smoke-bootstrap-project.py` passed.
