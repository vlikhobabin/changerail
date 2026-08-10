## 1. CI Template And Bootstrap

- [x] 1.1 Add the opt-in GitHub Actions consumer workflow template with
  read-only permissions and exact lock-driven checkout.
- [x] 1.2 Add `--with-ci` planning/rendering and fail-before-write validation for
  absent, malformed or non-strict locks.
- [x] 1.3 Implement disposable lock-owned wiring repair and the documented local
  consumer baseline command sequence.

## 2. Deterministic Regression Evidence

- [x] 2.1 Add structured workflow contract smoke for triggers, permissions,
  exact revision, no-auth baseline and no-publish behavior.
- [x] 2.2 Add a local clean-clone fixture using disposable Git repositories that
  fails against the current no-template behavior before implementation.
- [x] 2.3 Cover unavailable revision, advisory/malformed lock and wiring conflict
  negative cases.

## 3. Release Integration And Docs

- [x] 3.1 Add focused consumer CI smoke to release baseline and tracked CI
  inventory.
- [x] 3.2 Document lock refresh, provider-neutral equivalent steps and failure
  remediation in adoption/release docs.

## 4. Verification

- [x] 4.1 Run focused consumer CI/bootstrap smoke and observe all positive and
  negative fixtures pass.
- [x] 4.2 Run `python3 scripts/run-release-baseline.py` and observe the full
  baseline pass.
- [x] 4.3 Run `./bin/openspec validate --all --strict`, current/history
  public-surface scans and `git diff --check`.
