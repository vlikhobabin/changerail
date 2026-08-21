## 1. Regression and implementation

- [x] 1.1 Add retained focused RED coverage that invokes the real tracked
  `bin/codex` through a fake Codex binary and fails while the explicit trusted
  home child argv lacks invocation-level authority.
- [x] 1.2 Add fail-closed Codex CLI capability preflight for the exact explicit
  operator-home plus tracked-launcher route.
- [x] 1.3 Propagate the invocation-level authority option before `exec` only on
  that route, preserving default generated-home and custom-launcher argv.
- [x] 1.4 Add GREEN coverage for runner status argv, launcher-observed argv,
  unsupported CLI blocking and unchanged non-opted-in routes.

## 2. Durable contract and verification

- [x] 2.1 Sync the delivery-runner capability and update durable runner docs
  with the narrow authority boundary, operational warning and consumer impact.
- [x] 2.2 Run `python3 scripts/smoke-delivery-runner.py` and record the observed
  outcome.
- [x] 2.3 Run `bin/openspec validate --all --strict`, `git diff --check` and
  `python3 scripts/public-surface-scan.py`.
- [x] 2.4 Run `python3 scripts/run-release-baseline.py` immediately before
  review handoff and retain concise evidence.
- [x] 2.5 Reconcile the delivery manifest to exact card-owned working-tree
  scope, archive the change after spec sync and hand off to fresh critical/xhigh
  review.
