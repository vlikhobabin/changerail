## 1. Review History And Metrics

- [x] 1.1 Add runtime review-cycle history schema/docs while preserving canonical latest verdict behavior.
- [x] 1.2 Add a tracked metrics helper that reads delivery run records and review-cycle evidence.
- [x] 1.3 Support text and CSV output with explicit `unknown` values for missing optional fields.

## 2. Methodology Docs

- [x] 2.1 Update methodology/how-it-works docs with the `over-claim -> no-go -> scoped rescue -> re-review -> go -> pub` flow.
- [x] 2.2 Update review skill guidance to retain review-cycle evidence without editing reviewed payload.

## 3. Verification

- [x] 3.1 Run `python3 scripts/smoke-delivery-metrics.py`.
- [x] 3.2 Run JSON schema parsing checks for new observability schemas.
- [x] 3.3 Run `./bin/openspec validate add-delivery-observability --strict`.
- [x] 3.4 Run `git diff --check`.
