## 1. Authorization Source

- [x] 1.1 Keep the authorization card out of `4.done` during delivery; publish
  finalization moves it only after the investigation dependency is published
  and verified.
- [x] 1.2 Publish exactly one machine-readable authorization object on the card
  with investigation id `investigate-runner-retained-resume-payload-boundary`,
  successor id `support-runner-resume-after-investigation-required`,
  production LOC ceiling 500 and protocol allowance true.
- [x] 1.3 Keep the payload scoped to board/OpenSpec documentation unless
  focused preflight coverage is missing.

## 2. Preflight Consumption

- [x] 2.1 Confirm the successor card references the published authorization
  source with exact `authorization_card` and `authorization_id` values.
- [x] 2.2 Confirm reciprocal relation checks pass only for the exact published
  investigation, authorization source and successor card chain.
- [x] 2.3 Add or update minimal focused smoke coverage if existing preflight
  tests do not prove exact successor acceptance and mismatched-card rejection.

## 3. Verification

- [x] 3.1 Run `./bin/openspec validate "authorize-bounded-runner-retained-resume-payload" --strict`.
- [x] 3.2 Run focused deterministic preflight or smoke verification for the
  exact successor authorization path.
- [x] 3.3 Run `./bin/openspec validate --all --strict`.
- [x] 3.4 Run `python3 scripts/public-surface-scan.py`.
- [x] 3.5 Run `git diff --check`.
