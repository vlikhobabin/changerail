## 1. Contract And Helper

- [x] 1.1 Update `schemas/changerail-review-verdict.schema.json` with required
  reviewer independence attestation.
- [x] 1.2 Update `scripts/changerail_review_verdict.py` validation for
  attestation shape and truth values.
- [x] 1.3 Update review verdict reference docs and `changerail-review` skill.
- [x] 1.4 Update contract docs/specs to document the guarantee and limit.

## 2. Smoke Coverage

- [x] 2.1 Add or update smoke coverage for valid attestation.
- [x] 2.2 Add negative smoke coverage for missing or false attestation.

## 3. Verification

- [x] 3.1 Run `python3 -m py_compile scripts/changerail_review_verdict.py`.
- [x] 3.2 Run `python3 scripts/smoke-review-fingerprint.py`.
- [x] 3.3 Run focused review-verdict validation smoke.
- [x] 3.4 Run `python3 -m json.tool schemas/changerail-review-verdict.schema.json`.
- [x] 3.5 Run `./bin/openspec validate "harden-review-independence-evidence" --strict`.
- [x] 3.6 Run `./bin/openspec validate --all --strict`.
- [x] 3.7 Run `git diff --check`.

## Verification Notes

- `python3 -m py_compile scripts/changerail_review_verdict.py scripts/smoke-review-verdict-validation.py bin/changerail-delivery-runner` passed.
- `python3 scripts/smoke-review-fingerprint.py` passed.
- `python3 scripts/smoke-review-verdict-validation.py` passed with
  `SMOKE_REVIEW_VERDICT_VALIDATION_OK`.
- `python3 -m json.tool schemas/changerail-review-verdict.schema.json` passed.
- `./bin/openspec validate harden-review-independence-evidence --strict` passed.
- `./bin/openspec validate --all --strict` passed with 17 items.
- `git diff --check` passed.
