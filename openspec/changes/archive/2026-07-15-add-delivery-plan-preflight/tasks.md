## 1. Runner Plan Resolution

- [x] 1.1 Add plan loading, schema validation and plan fingerprinting to `bin/changerail-delivery-runner`.
- [x] 1.2 Implement stable board card resolution by filename/card id across `openspec/board/*`.
- [x] 1.3 Implement DAG, wave, duplicate id, workspace and concurrency validation.

## 2. Preflight Commands

- [x] 2.1 Add `plan`, `preflight-plan` and `status-plan` CLI commands without changing existing `run` and `preflight`.
- [x] 2.2 Make dry-run output include resolved workspaces, cards, dependencies, waves and child runner commands.
- [x] 2.3 Write schema-backed aggregate status for successful and failed preflight.

## 3. Focused Smoke Coverage

- [x] 3.1 Add smoke coverage for valid dry-run/preflight/status output.
- [x] 3.2 Add fail-closed smoke cases for cycle, duplicate card/id, missing card/workspace/dependency, canceled card, invalid wave and invalid concurrency.
- [x] 3.3 Add compatibility smoke coverage proving single-card `run` and `preflight` behavior is unchanged.

## 4. Verification

- [x] 4.1 Run `python3 -m py_compile bin/changerail-delivery-runner`.
- [x] 4.2 Run `python3 scripts/smoke-delivery-runner.py`.
- [x] 4.3 Run `./bin/openspec validate add-delivery-plan-preflight --strict`.
- [x] 4.4 Run `./bin/openspec validate --all --strict`.
- [x] 4.5 Run `git diff --check`, including new untracked files.
