## 1. Designer XML Measurement

- [x] 1.1 Depend on the source-classification loader from
  `define-review-preflight-source-classification`.
- [x] 1.2 Implement a Designer XML `xml-structure` measure strategy for
  classified production XML.
- [x] 1.3 Fall back to raw added lines or block preflight when classified XML
  cannot be measured conservatively.
- [x] 1.4 Ensure generic XML schemas, templates, fixtures, examples, docs and
  OpenSpec files are not production by suffix alone.

## 2. Complexity Guard Integration

- [x] 2.1 Aggregate Designer XML effective complexity into
  `added_production_loc` without removing the existing guard field.
- [x] 2.2 Report raw added lines, effective complexity, measure strategy,
  counted path counts and fallback state in source-kind breakdown.
- [x] 2.3 Preserve default 300 and published-authorization ceiling behavior
  using effective complexity, with fail-closed reasons when exceeded.

## 3. Regression Coverage

- [x] 3.1 Add synthetic temporary XML smoke cases for declared production
  Designer XML and unclassified generic XML.
- [x] 3.2 Add smoke coverage for verbose XML whose raw lines exceed the ceiling
  but structural complexity is within bounds.
- [x] 3.3 Add smoke coverage for malformed or unmeasurable classified XML
  fallback/block behavior.
- [x] 3.4 Add a mixed BSL and Designer XML payload smoke that asserts separate
  source-kind breakdown entries.

## 4. Docs And Specs

- [x] 4.1 Update `docs/changerail-contracts.md` with Designer XML effective
  complexity semantics.
- [x] 4.2 Update `schemas/changerail-review-preflight-result.schema.json` if
  needed for XML measure/fallback fields.
- [x] 4.3 Sync the `changerail-contracts` spec after implementation.

## 5. Verification

- [x] 5.1 Run `python3 -m py_compile scripts/changerail_review_preflight.py`.
- [x] 5.2 Run `python3 scripts/smoke-contract-schemas.py`.
- [x] 5.3 Run `python3 scripts/smoke-review-preflight.py`.
- [x] 5.4 Run `./bin/openspec validate "measure-review-preflight-designer-xml" --strict`.
- [x] 5.5 Run `./bin/openspec validate --all --strict`.
- [x] 5.6 Run `git diff --check`.
- [x] 5.7 Run `python3 scripts/public-surface-scan.py`.
