## 1. BSL Classification And Counting

- [x] 1.1 Depend on the source-classification loader from
  `define-review-preflight-source-classification`.
- [x] 1.2 Count `.bsl` added lines under declared production BSL roots with the
  `lines` measure strategy.
- [x] 1.3 Ensure `test`, `tests`, `fixtures`, `examples`, `schemas`,
  `templates`, `docs` and `openspec` path parts still exclude BSL files from
  production complexity.
- [x] 1.4 Preserve existing production counting for built-in language suffixes,
  Go `*_test.go` exclusion and executable helpers.

## 2. Regression Coverage

- [x] 2.1 Add a synthetic temporary-repository smoke case that demonstrates the
  current false-negative for more than 300 production `.bsl` lines.
- [x] 2.2 Add GREEN smoke cases for declared production BSL, non-production BSL
  exclusions and mixed existing language payloads.
- [x] 2.3 Assert source-kind breakdown identifies the BSL contribution without
  storing real BSL source fixtures.

## 3. Docs And Specs

- [x] 3.1 Update `docs/changerail-contracts.md` with BSL production
  classification behavior.
- [x] 3.2 Sync the `changerail-contracts` spec after implementation.

## 4. Verification

- [x] 4.1 Run `python3 -m py_compile scripts/changerail_review_preflight.py`.
- [x] 4.2 Run `python3 scripts/smoke-review-preflight.py`.
- [x] 4.3 Run `./bin/openspec validate "count-review-preflight-bsl-production-loc" --strict`.
- [x] 4.4 Run `./bin/openspec validate --all --strict`.
- [x] 4.5 Run `git diff --check`.
- [x] 4.6 Run `python3 scripts/public-surface-scan.py`.
