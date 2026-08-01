## 1. Schemas and contracts
- [x] Extend `schemas/changerail-delivery-run.schema.json` preflight check
  entries with optional sanitized remote preflight evidence fields.
- [x] Extend `schemas/changerail-delivery-plan-status.schema.json` queue card
  entries if needed for compact child remote failure class evidence.
- [x] Update `docs/changerail-contracts.md` and compatibility/operator docs for
  remote preflight classes, retry/backoff and explicit resume.

## 2. Runner behavior
- [x] Refactor `bin/changerail-delivery-runner` remote-push publish target
  proof into classifiable sanitized attempt/evidence helpers.
- [x] Classify SSH config, DNS, auth, missing branch, timeout and unknown
  remote failures.
- [x] Add bounded retry/backoff only for transient classes.
- [x] Add explicit single-card `resume` that reads prior status, repeats full
  fresh preflight and launches only after publish target proof passes.
- [x] Propagate child remote preflight class through queue preflight/status
  without raw child logs.

## 3. Verification
- [x] Add smoke coverage for each remote failure class without external
  network dependency.
- [x] Add smoke coverage for later-success explicit resume without external
  network dependency.
- [x] Add or update schema smoke fixtures for remote preflight evidence.
- [x] Run `python3 scripts/smoke-delivery-runner.py`.
- [x] Run `python3 scripts/smoke-contract-schemas.py`.
- [x] Run `python3 scripts/smoke-delivery-manifest.py`.
- [x] Run `./bin/openspec validate add-remote-preflight-diagnostics-and-resume --strict`.
- [x] Run `./bin/openspec validate --all --strict`.
- [x] Run `git diff --check`.
- [x] Run `python3 scripts/public-surface-scan.py`.
- [x] Run `python3 scripts/run-release-baseline.py`.
