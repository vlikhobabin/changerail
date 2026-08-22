## 1. Profile schema and checksum

- [x] 1.1 Add RED schema fixtures for safe built-in/local profiles, unsafe
  paths, commands/URLs/imports, unsupported measures and malformed detection
  signals.
- [x] 1.2 Add `changerail.source-classification-profile.v1` and canonical JSON
  checksum helper with same-id/version checksum conflict detection.
- [x] 1.3 Extend `changerail.source-classification.v1` with optional ordered
  provenance and exact normalized override paths while preserving legacy files.

## 2. Registry and merge

- [x] 2.1 Add a tracked data-only generic built-in profile directory and validate
  every profile through the public schema at release time.
- [x] 2.2 Implement explicit local profile loading that reports source kind and
  checksum without executing code, accessing network or retaining absolute path.
- [x] 2.3 Implement deterministic multi-profile merge, equivalent deduplication,
  canonical sorting and fail-closed id/measurement/root conflicts.
- [x] 2.4 Add synthetic compatible, mixed-stack, immutable-version and
  conflicting-measure fixtures.

## 3. Documentation and verification

- [x] 3.1 Add profile/provenance/checksum schemas and built-in data to public
  contract inventory and docs.
- [x] 3.2 Run `python3 scripts/smoke-contract-schemas.py` and observe profile,
  provenance, merge conflict and legacy classification fixtures pass.
- [x] 3.3 Run `python3 scripts/smoke-review-preflight.py` and observe existing
  classification behavior remains unchanged with/without optional provenance.
- [x] 3.4 Run `bin/openspec validate --all --strict`, `git diff --check` and
  `python3 scripts/public-surface-scan.py`; retain outputs only in ignored
  runtime evidence.
