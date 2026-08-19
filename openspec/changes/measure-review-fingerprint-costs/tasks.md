## 1. Measurement Instrumentation

- [ ] 1.1 Add opt-in timing collection to the review fingerprint helper without
  changing default `fingerprint` JSON fields.
- [ ] 1.2 Add review preflight timing around fingerprint, OpenSpec validation,
  scoped whitespace check and public-surface scan.
- [ ] 1.3 Keep timing output public-safe by avoiding absolute private consumer
  paths and raw command logs.

## 2. Synthetic Benchmark

- [ ] 2.1 Add a synthetic large-repository smoke/benchmark for docs-only and
  source payloads.
- [ ] 2.2 Record phase timings and threshold rationale from the synthetic
  fixture.
- [ ] 2.3 Wire focused benchmark coverage into the relevant release or smoke
  baseline without making it too slow for ordinary verification.

## 3. Verification

- [ ] 3.1 Run `python3 -m py_compile scripts/changerail_review_verdict.py scripts/changerail_review_preflight.py`.
- [ ] 3.2 Run `python3 scripts/smoke-review-fingerprint.py`.
- [ ] 3.3 Run `python3 scripts/smoke-review-preflight.py`.
- [ ] 3.4 Run the new synthetic benchmark smoke.
- [ ] 3.5 Run `./bin/openspec validate "measure-review-fingerprint-costs" --strict`.
- [ ] 3.6 Run `./bin/openspec validate --all --strict`.
- [ ] 3.7 Run `git diff --check`.
