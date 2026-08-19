## 1. Source Classification Contract

- [ ] 1.1 Add schema-backed loading for optional `.changerail/source-classification.yaml`.
- [ ] 1.2 Reject absolute paths, traversal, duplicate source-kind ids and
  schema-invalid classification values fail-closed.
- [ ] 1.3 Preserve existing built-in production suffix and executable-helper
  behavior when the file is absent.
- [ ] 1.4 Add a public schema or documented validation contract for
  `changerail.source-classification.v1`.

## 2. Preflight Result Detail

- [ ] 2.1 Extend complexity calculation to return bounded source-kind
  breakdown metadata alongside `added_production_loc`.
- [ ] 2.2 Update `schemas/changerail-review-preflight-result.schema.json` and
  schema smoke fixtures for the new breakdown.
- [ ] 2.3 Keep raw source content, ignored runtime files and private data out
  of preflight results.

## 3. Docs And Templates

- [ ] 3.1 Document `.changerail/source-classification.yaml` in
  `docs/changerail-contracts.md`.
- [ ] 3.2 Update generated consumer guidance/templates to explain the optional
  project-owned classification file without domain-specific defaults.
- [ ] 3.3 Add focused smoke cases for missing, valid and invalid
  source-classification files.

## 4. Verification

- [ ] 4.1 Run `python3 -m py_compile scripts/changerail_review_preflight.py scripts/changerail_contract_schema.py`.
- [ ] 4.2 Run `python3 scripts/smoke-contract-schemas.py`.
- [ ] 4.3 Run `python3 scripts/smoke-review-preflight.py`.
- [ ] 4.4 Run `./bin/openspec validate "define-review-preflight-source-classification" --strict`.
- [ ] 4.5 Run `./bin/openspec validate --all --strict`.
- [ ] 4.6 Run `git diff --check`.
- [ ] 4.7 Run `python3 scripts/public-surface-scan.py`.
