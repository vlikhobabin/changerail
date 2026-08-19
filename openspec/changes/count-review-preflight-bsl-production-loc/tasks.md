## 1. BSL Classification And Counting

- [ ] 1.1 Depend on the source-classification loader from
  `define-review-preflight-source-classification`.
- [ ] 1.2 Count `.bsl` added lines under declared production BSL roots with the
  `lines` measure strategy.
- [ ] 1.3 Ensure `test`, `tests`, `fixtures`, `examples`, `schemas`,
  `templates`, `docs` and `openspec` path parts still exclude BSL files from
  production complexity.
- [ ] 1.4 Preserve existing production counting for built-in language suffixes,
  Go `*_test.go` exclusion and executable helpers.

## 2. Regression Coverage

- [ ] 2.1 Add a synthetic temporary-repository smoke case that demonstrates the
  current false-negative for more than 300 production `.bsl` lines.
- [ ] 2.2 Add GREEN smoke cases for declared production BSL, non-production BSL
  exclusions and mixed existing language payloads.
- [ ] 2.3 Assert source-kind breakdown identifies the BSL contribution without
  storing real BSL source fixtures.

## 3. Docs And Specs

- [ ] 3.1 Update `docs/changerail-contracts.md` with BSL production
  classification behavior.
- [ ] 3.2 Sync the `changerail-contracts` spec after implementation.

## 4. Verification

- [ ] 4.1 Run `python3 -m py_compile scripts/changerail_review_preflight.py`.
- [ ] 4.2 Run `python3 scripts/smoke-review-preflight.py`.
- [ ] 4.3 Run `./bin/openspec validate "count-review-preflight-bsl-production-loc" --strict`.
- [ ] 4.4 Run `./bin/openspec validate --all --strict`.
- [ ] 4.5 Run `git diff --check`.
- [ ] 4.6 Run `python3 scripts/public-surface-scan.py`.
