## 1. Fixture Implementation

- [x] 1.1 Extend the delivery runner smoke fixtures with a temporary
      deliver-ready workspace, local bare remote and test-only fake
      one-command delivery launcher.
- [x] 1.2 Add the success scenario assertions for final card state, Git history,
      remote branch, manifest, verdict, retained evidence, runner status and
      extra-scope exclusion.
- [x] 1.3 Add the transient preflight stop and explicit resume scenario.
- [x] 1.4 Add fail-closed stale-verdict and exhausted review-budget scenarios.

## 2. Release Inventory

- [x] 2.1 Update the local release baseline or delivery-runner smoke inventory
      so one-command regression coverage is included in
      `python3 scripts/run-release-baseline.py`.
- [x] 2.2 Update durable release documentation to list the new coverage.

## 3. Verification

- [x] 3.1 Run `python3 scripts/smoke-delivery-runner.py`.
- [x] 3.2 Run `./bin/openspec validate --all --strict`.
- [x] 3.3 Run `python3 scripts/run-release-baseline.py`.
- [x] 3.4 Run `python3 scripts/public-surface-scan.py` and
      `python3 scripts/public-surface-scan.py --history`.
- [x] 3.5 Run `git diff --check`.
