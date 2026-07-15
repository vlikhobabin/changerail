## 1. Live Queue Execution

- [x] 1.1 Implement `run-plan` over the existing single-card runner with one child run record per card.
- [x] 1.2 Enforce wave and dependency barriers plus workspace serialization with bounded cross-workspace parallelism.
- [x] 1.3 Implement fail-fast handling for child `NO-GO`, `BLOCKED`, stale/invalid verdict, push rejection, unexpected dirty scope and inconsistent card state.

## 2. Resume And Locks

- [x] 2.1 Add ignored workspace locks and stale-lock diagnostics without unsafe automatic deletion.
- [x] 2.2 Implement `resume-plan` fingerprint checks, successful-card skip logic and board re-resolution for unfinished cards.
- [x] 2.3 Implement push-enabled and explicit `--no-push` success criteria in aggregate status.

## 3. Metrics And Docs

- [x] 3.1 Extend `bin/changerail-delivery-metrics` and smoke fixtures to read queue status plus child run records.
- [x] 3.2 Update public docs for plan creation, list/preflight/dry-run/live/resume/status, locks, terminal outcomes and push/no-push success.
- [x] 3.3 Update methodology/compatibility docs to describe the tracked queue runner without changing single-card runner usage.

## 4. Verification

- [x] 4.1 Run `python3 -m py_compile bin/changerail-delivery-runner bin/changerail-delivery-metrics`.
- [x] 4.2 Run `python3 scripts/smoke-delivery-runner.py`.
- [x] 4.3 Run `python3 scripts/smoke-delivery-metrics.py`.
- [x] 4.4 Run `python3 scripts/smoke-contract-schemas.py`.
- [x] 4.5 Run `./bin/openspec validate add-delivery-plan-run-resume --strict`.
- [x] 4.6 Run `./bin/openspec validate --all --strict`.
- [x] 4.7 Run `python3 scripts/public-surface-scan.py`.
- [x] 4.8 Run `python3 scripts/run-release-baseline.py`.
