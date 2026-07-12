## 1. Baseline command
- [x] Add `scripts/run-release-baseline.py` or an equivalent tracked local
  release command.
- [x] Make the command run the same mandatory checks as release CI, including
  generated drift fixture coverage and public-surface scans.
- [x] Ensure the command returns non-zero on first mandatory failure and prints
  concrete command/outcome evidence.

## 2. CI and docs
- [x] Invoke the local baseline from CI after dependency setup, or keep an
  equivalent command inventory checked by `scripts/smoke-release-ci.py`.
- [x] Document the command in `docs/release-discipline.md`, `README.md` and
  repository verification guidance.
- [x] Document that no-argument `scripts/smoke-drift.py` remains invalid without
  `--config`, `--workspace-root` or `--project`.

## 3. Verification
- [x] Run `python3 scripts/run-release-baseline.py` and record the outcome.
  Outcome: pass, 25/25 baseline steps passed.
- [x] Run `openspec validate add-local-release-baseline --strict`.
  Outcome: pass.
