## 1. Runner Contract

- [x] 1.1 Add `opsx.delivery-run.v1` JSON schema for runtime status/run records.
- [x] 1.2 Add a tracked `bin/opsx-delivery-runner` helper that launches `codex exec` through the repo launcher, closes stdin and writes atomic status JSON.
- [x] 1.3 Support per-run model and reasoning effort options without changing repo defaults.
- [x] 1.4 Implement preflight checks for launcher, effective `CODEX_HOME`, executable permissions and optional connectivity URL.

## 2. Docs And Tests

- [x] 2.1 Document the runner contract and preflight/runbook in public docs.
- [x] 2.2 Add smoke tests for command construction, closed stdin, terminal status and preflight behavior using generic fixtures.

## 3. Verification

- [x] 3.1 Run `python3 scripts/smoke-delivery-runner.py`.
- [x] 3.2 Run JSON schema parsing checks for `schemas/opsx-delivery-run.schema.json`.
- [x] 3.3 Run `./bin/openspec validate add-generic-delivery-runner --strict`.
- [x] 3.4 Run `git diff --check`.
