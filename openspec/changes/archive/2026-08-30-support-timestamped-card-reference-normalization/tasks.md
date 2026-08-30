## 1. Semantic RED

- [x] 1.1 Add matcher assertions for the three exact timestamped reference
  forms and malformed/mixed-case negative cases; retain assertion-failure RED.
- [x] 1.2 Add a synthetic tracked-HEAD authorization chain whose investigation,
  authorization and successor all use sortable UTC ids.

## 2. Reference Grammar

- [x] 2.1 Add the bounded UTC timestamp card-id alternative to the three
  relation-reference regexes without changing general card discovery.
- [x] 2.2 Prove ordinary lowercase references and all existing authorization
  fixtures remain compatible.

## 3. Contracts And Verification

- [x] 3.1 Sync the modified `changerail-contracts` requirement and archive the
  change after focused smoke and strict OpenSpec validation.
- [x] 3.2 Run `python3 scripts/smoke-review-preflight.py`, contract-schema smoke,
  `ruff`, `py_compile`, public-surface current/history scans, strict OpenSpec,
  whitespace checks and `python3 scripts/run-release-baseline.py`.
- [x] 3.3 Derive and scope-check the delivery manifest, then pass normalized
  ordinary preflight for independent review.

## 4. Review Remediation

- [x] 4.1 Reject impossible UTC calendar dates, out-of-range times and year
  `0000` after the bounded lexical timestamp match.
- [x] 4.2 Retain and validate assertion-failure RED plus full-smoke GREEN under
  the card-owned ignored evidence index.
- [ ] 4.3 Rerun the complete release floor, refresh manifest/preflight and pass
  independent review cycle 2.
