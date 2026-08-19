## 1. Authorization Source

- [ ] 1.1 Move the authorization card to `4.done` only after the investigation
  dependency is published and verified.
- [ ] 1.2 Publish exactly one machine-readable authorization object on the
  card with investigation id `investigate-bounded-review-fingerprint-payload`,
  successor id `deliver-bounded-review-fingerprint-optimization`,
  production LOC ceiling 500 and protocol allowance false.
- [ ] 1.3 Keep the payload scoped to board/OpenSpec documentation unless
  focused preflight coverage is missing.

## 2. Preflight Consumption

- [ ] 2.1 Confirm the successor card references the published authorization
  source with exact `authorization_card` and `authorization_id` values.
- [ ] 2.2 Confirm reciprocal relation checks pass only for the exact published
  investigation, authorization source and successor card chain.
- [ ] 2.3 Add or update minimal focused smoke coverage if existing preflight
  tests do not prove exact successor acceptance and mismatched-card rejection.

## 3. Verification

- [ ] 3.1 Run `./bin/openspec validate "authorize-bounded-review-fingerprint-payload" --strict`.
- [ ] 3.2 Run focused deterministic preflight or smoke verification for the
  exact successor authorization path.
- [ ] 3.3 Run `./bin/openspec validate --all --strict`.
- [ ] 3.4 Run `python3 scripts/public-surface-scan.py`.
- [ ] 3.5 Run `git diff --check`.
