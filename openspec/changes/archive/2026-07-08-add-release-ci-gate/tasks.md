## 1. CI Workflow

- [x] 1.1 Add `.github/workflows/opsx-ci.yml`.
- [x] 1.2 Include OpenSpec validation and docs/config baseline checks.
- [x] 1.3 Include Python syntax checks for scripts/helpers.
- [x] 1.4 Include wiring, verify-project and bootstrap smoke tests.
- [x] 1.5 Include drift smoke against a generated generic runtime fixture.

## 2. CI Contract Smoke

- [x] 2.1 Add `scripts/smoke-release-ci.py`.
- [x] 2.2 Make the smoke fail closed when required triggers or command strings
  are missing.
- [x] 2.3 Document CI in release docs or README.

## 3. Verification

- [x] 3.1 Run `python3 -m py_compile scripts/smoke-release-ci.py`.
- [x] 3.2 Run `python3 scripts/smoke-release-ci.py`.
- [x] 3.3 Run `openspec validate add-release-ci-gate --strict`.
- [x] 3.4 Run `openspec validate --all --strict`.
- [x] 3.5 Run docs/config baseline checks from `AGENTS.md`.

## Evidence

- `python3 -m py_compile scripts/smoke-release-ci.py` passed.
- `python3 scripts/smoke-release-ci.py` passed with 21/21 checks.
- `./bin/openspec validate --all --strict` passed with 11/11 items.
- `python3 -m py_compile bin/bootstrap-project bin/verify-project
  scripts/opsx_review_verdict.py scripts/smoke-bootstrap-project.py
  scripts/smoke-drift.py scripts/smoke-release-ci.py
  scripts/smoke-verify-project.py scripts/smoke-wiring-discovery.py` passed.
- `python3 scripts/smoke-wiring-discovery.py` passed with 118/118 checks.
- `python3 scripts/smoke-verify-project.py` passed with 2/2 checks.
- `python3 scripts/smoke-bootstrap-project.py` passed with 4/4 checks.
- Generated-fixture drift check passed:
  `./bin/bootstrap-project .runtime/opsx/ci-drift/example-project --name
  example-project --kind generic` followed by
  `python3 scripts/smoke-drift.py --project
  .runtime/opsx/ci-drift/example-project`.
- `openspec validate add-release-ci-gate --strict` passed.
- `openspec validate --all --strict` passed with 11/11 items.
- `python3 -m json.tool .mcp.json` passed.
- TOML parse for `.codex/config.toml` passed and printed `TOML_OK`.
- `git diff --check` passed.
